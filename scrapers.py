"""
Preisvergleich – Scraper-Klassen (ein Scraper pro Quelle)
"""
from __future__ import annotations

import base64
import json
import random
import re
import time
from dataclasses import dataclass
from urllib.parse import quote_plus

import requests

from config import (
    BROWSER_UA,
    EBAY_CLIENT_ID,
    EBAY_CLIENT_SECRET,
    MAX_RESULTS_PER_SOURCE,
    REQUEST_TIMEOUT,
)


@dataclass
class PriceResult:
    title: str
    price: float
    shipping: float
    total_price: float
    shop: str
    url: str
    image_url: str = ""
    condition: str = "neu"
    source: str = ""


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class BaseScraper:
    source_id: str = ""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": BROWSER_UA,
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.5",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "DNT": "1",
        })

    def _request(self, url: str, **kwargs) -> requests.Response | None:
        for attempt in range(2):
            try:
                resp = self.session.get(url, timeout=REQUEST_TIMEOUT, **kwargs)
                if resp.status_code == 200:
                    return resp
            except Exception:
                pass
            if attempt == 0:
                time.sleep(random.uniform(0.3, 0.8))
        return None

    def _parse_json_ld(self, html: str) -> list[dict]:
        blocks = re.findall(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html,
            re.DOTALL | re.IGNORECASE,
        )
        results: list[dict] = []
        for block in blocks:
            try:
                data = json.loads(block)
                if isinstance(data, list):
                    results.extend(data)
                else:
                    results.append(data)
            except (json.JSONDecodeError, ValueError):
                pass
        return results

    def _parse_price(self, text: str) -> float:
        # Handles "1.249,99 €", "199,99€", "1249.99", "ab 89,90 €"
        text = re.sub(r"[^\d,.]", "", text)
        # German format: dots as thousand separator, comma as decimal
        if "," in text and "." in text:
            text = text.replace(".", "").replace(",", ".")
        elif "," in text:
            text = text.replace(",", ".")
        try:
            return float(text)
        except ValueError:
            return 0.0

    def _make_result(
        self,
        title: str,
        price: float,
        shop: str,
        url: str,
        image_url: str = "",
        shipping: float = 0.0,
        condition: str = "neu",
    ) -> PriceResult | None:
        if not title or price <= 0:
            return None
        return PriceResult(
            title=title.strip(),
            price=price,
            shipping=shipping,
            total_price=round(price + shipping, 2),
            shop=shop,
            url=url,
            image_url=image_url,
            condition=condition,
            source=self.source_id,
        )

    def scrape(self, query: str) -> list[PriceResult]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Geizhals.de
# ---------------------------------------------------------------------------

class GeizhalsScaper(BaseScraper):
    source_id = "geizhals"

    def scrape(self, query: str) -> list[PriceResult]:
        time.sleep(random.uniform(0.5, 1.2))
        url = f"https://geizhals.de/?fs={quote_plus(query)}&hloc=de&sort=p&cc=de"
        resp = self._request(url, headers={"Referer": "https://geizhals.de/"})
        if not resp:
            return []

        results = self._from_json_ld(resp.text)
        if not results:
            results = self._from_regex(resp.text)
        return results[:MAX_RESULTS_PER_SOURCE]

    def _from_json_ld(self, html: str) -> list[PriceResult]:
        items = self._parse_json_ld(html)
        results: list[PriceResult] = []
        for item in items:
            if item.get("@type") not in ("Product", "ItemList"):
                continue
            offers = item.get("offers", {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            name = item.get("name", "")
            price_raw = offers.get("price", 0)
            try:
                price = float(price_raw)
            except (ValueError, TypeError):
                price = self._parse_price(str(price_raw))
            url = offers.get("url", item.get("url", ""))
            image = item.get("image", "")
            if isinstance(image, list):
                image = image[0] if image else ""
            r = self._make_result(name, price, "geizhals.de", url, image)
            if r:
                results.append(r)
        return results

    def _from_regex(self, html: str) -> list[PriceResult]:
        results: list[PriceResult] = []
        # Product card pattern on geizhals
        cards = re.findall(
            r'data-name="([^"]+)"[^>]*>.*?data-price="([^"]+)".*?href="(/[^"]+)"',
            html,
            re.DOTALL,
        )
        for name, price_str, path in cards:
            price = self._parse_price(price_str)
            url = f"https://geizhals.de{path}"
            r = self._make_result(name, price, "geizhals.de", url)
            if r:
                results.append(r)
        return results


# ---------------------------------------------------------------------------
# Alternate.de
# ---------------------------------------------------------------------------

class AlternateScraper(BaseScraper):
    source_id = "alternate"

    def scrape(self, query: str) -> list[PriceResult]:
        time.sleep(random.uniform(0.3, 0.8))
        url = f"https://www.alternate.de/search?query={quote_plus(query)}"
        resp = self._request(url, headers={"Referer": "https://www.alternate.de/"})
        if not resp:
            return []

        results = self._from_json_ld(resp.text)
        if not results:
            results = self._from_regex(resp.text)
        return results[:MAX_RESULTS_PER_SOURCE]

    def _from_json_ld(self, html: str) -> list[PriceResult]:
        items = self._parse_json_ld(html)
        results: list[PriceResult] = []
        for item in items:
            if item.get("@type") == "ItemList":
                for element in item.get("itemListElement", []):
                    item2 = element.get("item", element)
                    r = self._extract_product(item2)
                    if r:
                        results.append(r)
            elif item.get("@type") == "Product":
                r = self._extract_product(item)
                if r:
                    results.append(r)
        return results

    def _extract_product(self, item: dict) -> PriceResult | None:
        name = item.get("name", "")
        offers = item.get("offers", {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        price_raw = offers.get("price", 0)
        try:
            price = float(price_raw)
        except (ValueError, TypeError):
            price = self._parse_price(str(price_raw))
        url = item.get("url", offers.get("url", ""))
        image = item.get("image", "")
        if isinstance(image, list):
            image = image[0] if image else ""
        return self._make_result(name, price, "alternate.de", url, image)

    def _from_regex(self, html: str) -> list[PriceResult]:
        results: list[PriceResult] = []
        # Look for product tiles with price spans
        names = re.findall(r'class="[^"]*product[^"]*title[^"]*"[^>]*>([^<]+)<', html, re.IGNORECASE)
        prices = re.findall(r'class="[^"]*price[^"]*"[^>]*>\s*([\d.,]+)\s*€', html, re.IGNORECASE)
        urls = re.findall(r'href="(https://www\.alternate\.de/[^"]+)"', html)
        for i, (name, price_str) in enumerate(zip(names, prices)):
            price = self._parse_price(price_str)
            url = urls[i] if i < len(urls) else "https://www.alternate.de"
            r = self._make_result(name.strip(), price, "alternate.de", url)
            if r:
                results.append(r)
        return results


# ---------------------------------------------------------------------------
# Notebooksbilliger.de
# ---------------------------------------------------------------------------

class NotebooksbilligerScraper(BaseScraper):
    source_id = "notebooksbilliger"

    def scrape(self, query: str) -> list[PriceResult]:
        time.sleep(random.uniform(0.5, 1.0))
        url = f"https://www.notebooksbilliger.de/search?q={quote_plus(query)}"
        resp = self._request(url, headers={"Referer": "https://www.notebooksbilliger.de/"})
        if not resp:
            return []

        results = self._from_json_ld(resp.text)
        if not results:
            results = self._from_regex(resp.text)
        return results[:MAX_RESULTS_PER_SOURCE]

    def _from_json_ld(self, html: str) -> list[PriceResult]:
        items = self._parse_json_ld(html)
        results: list[PriceResult] = []
        for item in items:
            if item.get("@type") not in ("Product", "ItemList"):
                continue
            if item.get("@type") == "ItemList":
                for el in item.get("itemListElement", []):
                    r = self._extract_product(el.get("item", el))
                    if r:
                        results.append(r)
            else:
                r = self._extract_product(item)
                if r:
                    results.append(r)
        return results

    def _extract_product(self, item: dict) -> PriceResult | None:
        name = item.get("name", "")
        offers = item.get("offers", {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        try:
            price = float(offers.get("price", 0))
        except (ValueError, TypeError):
            price = self._parse_price(str(offers.get("price", "")))
        url = item.get("url", "")
        image = item.get("image", "")
        if isinstance(image, list):
            image = image[0] if image else ""
        return self._make_result(name, price, "notebooksbilliger.de", url, image)

    def _from_regex(self, html: str) -> list[PriceResult]:
        results: list[PriceResult] = []
        blocks = re.findall(
            r'<article[^>]+class="[^"]*product[^"]*"[^>]*>(.*?)</article>',
            html, re.DOTALL | re.IGNORECASE
        )
        for block in blocks:
            name_m = re.search(r'<[^>]+class="[^"]*product.?name[^"]*"[^>]*>([^<]+)<', block, re.IGNORECASE)
            price_m = re.search(r'([\d.,]+)\s*€', block)
            url_m = re.search(r'href="(https://www\.notebooksbilliger\.de/[^"]+)"', block)
            if name_m and price_m:
                name = name_m.group(1).strip()
                price = self._parse_price(price_m.group(1))
                url = url_m.group(1) if url_m else "https://www.notebooksbilliger.de"
                r = self._make_result(name, price, "notebooksbilliger.de", url)
                if r:
                    results.append(r)
        return results


# ---------------------------------------------------------------------------
# eBay Browse API (optional – benötigt App-ID + Cert-ID)
# ---------------------------------------------------------------------------

class EbayScraper(BaseScraper):
    source_id = "ebay"
    _token: str = ""
    _expires_at: float = 0.0

    def _get_token(self) -> str:
        if time.time() < self._expires_at and self._token:
            return self._token
        creds = base64.b64encode(
            f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}".encode()
        ).decode()
        try:
            resp = self.session.post(
                "https://api.ebay.com/identity/v1/oauth2/token",
                headers={
                    "Authorization": f"Basic {creds}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data="grant_type=client_credentials&scope=https%3A%2F%2Fapi.ebay.com%2Foauth%2Fapi_scope",
                timeout=REQUEST_TIMEOUT,
            )
            data = resp.json()
            self._token = data["access_token"]
            self._expires_at = time.time() + data.get("expires_in", 7200) - 60
        except Exception:
            self._token = ""
        return self._token

    def scrape(self, query: str) -> list[PriceResult]:
        if not EBAY_CLIENT_ID:
            return []
        token = self._get_token()
        if not token:
            return []
        try:
            resp = self.session.get(
                "https://api.ebay.com/buy/browse/v1/item_summary/search",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-EBAY-C-MARKETPLACE-ID": "EBAY_DE",
                    "Content-Language": "de-DE",
                },
                params={
                    "q": query,
                    "filter": "deliveryCountry:DE,itemLocationCountry:DE",
                    "sort": "price",
                    "limit": MAX_RESULTS_PER_SOURCE,
                },
                timeout=REQUEST_TIMEOUT,
            )
            items = resp.json().get("itemSummaries", [])
        except Exception:
            return []

        results: list[PriceResult] = []
        for item in items:
            name = item.get("title", "")
            price_obj = item.get("price", {})
            try:
                price = float(price_obj.get("value", 0))
            except (ValueError, TypeError):
                continue
            shipping_obj = (item.get("shippingOptions") or [{}])[0]
            try:
                shipping = float(shipping_obj.get("shippingCost", {}).get("value", 0))
            except (ValueError, TypeError):
                shipping = 0.0
            url = item.get("itemWebUrl", "")
            image = item.get("image", {}).get("imageUrl", "")
            condition = item.get("condition", "neu").lower()
            r = self._make_result(name, price, "ebay.de", url, image, shipping, condition)
            if r:
                results.append(r)
        return results


# ---------------------------------------------------------------------------
# Open Food Facts API (Lebensmittel – keine Auth nötig)
# ---------------------------------------------------------------------------

class OpenFoodFactsScraper(BaseScraper):
    source_id = "openfoodfacts"

    def scrape(self, query: str) -> list[PriceResult]:
        try:
            resp = self.session.get(
                "https://world.openfoodfacts.org/cgi/search.pl",
                params={
                    "search_terms": query,
                    "action": "process",
                    "json": "1",
                    "page_size": "20",
                    "lc": "de",
                },
                timeout=REQUEST_TIMEOUT,
                headers={"User-Agent": BROWSER_UA},
            )
            products = resp.json().get("products", [])
        except Exception:
            return []

        results: list[PriceResult] = []
        for product in products:
            name = (
                product.get("product_name_de")
                or product.get("product_name")
                or product.get("generic_name", "")
            ).strip()
            if not name:
                continue

            # Preis: Open Food Facts hat selten Preise; falls vorhanden nutzen, sonst überspringen
            price_raw = product.get("price") or product.get("price_per_unit", "")
            if not price_raw:
                continue
            price = self._parse_price(str(price_raw))
            if price <= 0:
                continue

            shops_raw = product.get("stores", "")
            shop = shops_raw.split(",")[0].strip() if shops_raw else "Open Food Facts"
            url = f"https://world.openfoodfacts.org/product/{product.get('code', '')}"
            image = product.get("image_small_url", product.get("image_url", ""))
            r = self._make_result(name, price, shop or "Open Food Facts", url, image)
            if r:
                results.append(r)
        return results[:MAX_RESULTS_PER_SOURCE]

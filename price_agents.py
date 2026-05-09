"""
Preisvergleich – Multi-Agent-Pipeline
Konsistentes Muster mit damage_agents.py
"""
from __future__ import annotations

import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from typing import Optional

from config import SOURCE_CONFIGS
from scrapers import (
    AlternateScraper,
    EbayScraper,
    GeizhalsScaper,
    NotebooksbilligerScraper,
    OpenFoodFactsScraper,
    PriceResult,
)


# ---------------------------------------------------------------------------
# Sub-Agent 1: Search-Agent  (Analyse der Suchanfrage)
# ---------------------------------------------------------------------------

class SearchAgent:
    """Analysiert die Suchanfrage und erkennt Kategorie + Typ."""

    FOOD_KEYWORDS = {
        "kaffee", "tee", "schokolade", "joghurt", "bier", "wein", "saft",
        "milch", "butter", "käse", "wurst", "brot", "mehl", "zucker", "öl",
        "nudeln", "reis", "müsli", "chips", "nuss", "nüsse", "cola", "wasser",
    }

    ELECTRONICS_KEYWORDS = {
        "laptop", "notebook", "smartphone", "handy", "tablet", "monitor",
        "drucker", "festplatte", "ssd", "ram", "gpu", "grafikkarte", "cpu",
        "prozessor", "headset", "kopfhörer", "lautsprecher", "kamera", "tv",
        "fernseher", "router", "usb", "hub",
    }

    def run(self, query: str) -> dict:
        tokens = query.lower().split()
        is_food = any(t in self.FOOD_KEYWORDS for t in tokens)
        is_electronics = any(t in self.ELECTRONICS_KEYWORDS for t in tokens)
        if is_food:
            category = "food"
        elif is_electronics:
            category = "electronics"
        else:
            category = "general"
        return {
            "normalized": query.strip(),
            "tokens": tokens,
            "is_food": is_food,
            "category": category,
        }


# ---------------------------------------------------------------------------
# Sub-Agent 2: Scraper-Agent  (paralleles Abfragen aller Quellen)
# ---------------------------------------------------------------------------

class ScraperAgent:
    """Fragt alle aktivierten Quellen parallel ab."""

    def __init__(self) -> None:
        self._scrapers: dict[str, object] = {
            "geizhals": GeizhalsScaper(),
            "alternate": AlternateScraper(),
            "notebooksbilliger": NotebooksbilligerScraper(),
            "ebay": EbayScraper(),
            "openfoodfacts": OpenFoodFactsScraper(),
        }

    def run(self, query: str, requested_sources: list[str]) -> list[PriceResult]:
        active = [
            s for s in requested_sources
            if s in self._scrapers and SOURCE_CONFIGS.get(s, {}).get("enabled", False)
        ]
        if not active:
            return []

        results: list[PriceResult] = []
        with ThreadPoolExecutor(max_workers=len(active)) as pool:
            futures = {
                pool.submit(self._scrapers[s].scrape, query): s
                for s in active
            }
            for future in as_completed(futures, timeout=20):
                source = futures[future]
                try:
                    batch = future.result()
                    results.extend(batch)
                except Exception:
                    pass  # Quelle antwortet nicht → still weitermachen
        return results


# ---------------------------------------------------------------------------
# Sub-Agent 3: Normalizer-Agent  (bereinigen & deduplizieren)
# ---------------------------------------------------------------------------

class NormalizerAgent:
    """Bereinigt Ergebnisse und entfernt Duplikate."""

    def run(self, results: list[PriceResult], analysis: dict) -> list[PriceResult]:
        cleaned = [r for r in results if r.total_price > 0 and r.title]
        cleaned = self._filter_relevance(cleaned, analysis)
        cleaned = self._deduplicate(cleaned)
        return cleaned

    def _filter_relevance(self, results: list[PriceResult], analysis: dict) -> list[PriceResult]:
        tokens = set(analysis.get("tokens", []))
        if not tokens:
            return results
        filtered = []
        for r in results:
            title_lower = r.title.lower()
            # Mindestens ein Suchtoken muss im Titel vorkommen
            if any(t in title_lower for t in tokens if len(t) > 2):
                filtered.append(r)
        return filtered if filtered else results  # Fallback: alles behalten

    def _deduplicate(self, results: list[PriceResult]) -> list[PriceResult]:
        seen: dict[str, PriceResult] = {}
        for r in results:
            key = self._normalize_title(r.title)
            if key not in seen or r.total_price < seen[key].total_price:
                seen[key] = r
        return list(seen.values())

    def _normalize_title(self, title: str) -> str:
        # Kleinschreibung, Sonderzeichen entfernen, auf 40 Zeichen kürzen
        import re
        clean = re.sub(r"[^a-z0-9 ]", "", title.lower())
        return " ".join(clean.split())[:40]


# ---------------------------------------------------------------------------
# Sub-Agent 4: Ranker-Agent  (sortieren + Hidden Gems finden)
# ---------------------------------------------------------------------------

class RankerAgent:
    """Sortiert nach Preis und hebt günstige Alternativen hervor."""

    # Gut bekannte Marken – Hidden Gems sind Produkte, die NICHT davon sind
    KNOWN_BRANDS = {
        "samsung", "lg", "sony", "apple", "bosch", "siemens", "philips",
        "dell", "hp", "lenovo", "asus", "acer", "microsoft", "huawei",
        "nikon", "canon", "dyson", "miele", "braun", "panasonic", "sharp",
        "jbl", "bose", "akg", "sennheiser", "logitech", "razer", "corsair",
    }

    def run(self, results: list[PriceResult]) -> dict:
        if not results:
            return {
                "results": [],
                "hidden_gems": [],
                "stats": {"min": 0, "max": 0, "median": 0, "count": 0},
            }

        sorted_results = sorted(results, key=lambda r: r.total_price)
        prices = [r.total_price for r in sorted_results]
        med = statistics.median(prices)

        hidden_gems = self._find_hidden_gems(sorted_results, med)

        return {
            "results": [asdict(r) for r in sorted_results],
            "hidden_gems": [asdict(g) for g in hidden_gems],
            "stats": {
                "min": round(min(prices), 2),
                "max": round(max(prices), 2),
                "median": round(med, 2),
                "count": len(sorted_results),
            },
        }

    def _find_hidden_gems(self, results: list[PriceResult], median: float) -> list[PriceResult]:
        gems = []
        for r in results:
            is_cheap = r.total_price <= median * 0.85
            brand = r.title.lower().split()[0] if r.title else ""
            is_unknown_brand = brand not in self.KNOWN_BRANDS
            if is_cheap and is_unknown_brand:
                gems.append(r)
            if len(gems) >= 4:
                break
        return gems


# ---------------------------------------------------------------------------
# Master-Agent  (orchestriert alle Sub-Agents)
# ---------------------------------------------------------------------------

class PriceMasterAgent:
    """Orchestriert die vollständige Preisvergleichs-Pipeline."""

    def __init__(self) -> None:
        self.search_agent = SearchAgent()
        self.scraper_agent = ScraperAgent()
        self.normalizer = NormalizerAgent()
        self.ranker = RankerAgent()

    def search(self, query: str, sources: Optional[list[str]] = None) -> dict:
        t0 = time.time()

        if not query or not query.strip():
            return {"error": "Bitte Suchbegriff eingeben", "results": [], "hidden_gems": [], "stats": {}}

        # Alle aktivierten Quellen wenn keine Auswahl getroffen
        if not sources:
            sources = [k for k, v in SOURCE_CONFIGS.items() if v.get("enabled")]

        analysis = self.search_agent.run(query)
        raw = self.scraper_agent.run(query, sources)
        normalized = self.normalizer.run(raw, analysis)
        ranked = self.ranker.run(normalized)

        ranked["query"] = query
        ranked["sources_used"] = sources
        ranked["category"] = analysis["category"]
        ranked["duration_ms"] = int((time.time() - t0) * 1000)
        return ranked

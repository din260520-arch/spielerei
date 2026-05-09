"""
Preisvergleich – Konfiguration
"""
import os

PORT = 8765
REQUEST_TIMEOUT = 10
MAX_RESULTS_PER_SOURCE = 20
CACHE_TTL = 300  # Sekunden

EBAY_CLIENT_ID     = os.environ.get("EBAY_CLIENT_ID", "")
EBAY_CLIENT_SECRET = os.environ.get("EBAY_CLIENT_SECRET", "")

BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"
)

SOURCE_CONFIGS = {
    "geizhals": {
        "name": "Geizhals.de",
        "enabled": True,
        "type": "scraper",
        "search_url": "https://geizhals.de/?fs={query}&hloc=de&sort=p&cc=de",
        "color": "#e67e22",
    },
    "alternate": {
        "name": "Alternate.de",
        "enabled": True,
        "type": "scraper",
        "search_url": "https://www.alternate.de/search?query={query}",
        "color": "#e74c3c",
    },
    "notebooksbilliger": {
        "name": "NBK.de",
        "enabled": True,
        "type": "scraper",
        "search_url": "https://www.notebooksbilliger.de/search?q={query}",
        "color": "#3498db",
    },
    "ebay": {
        "name": "eBay.de",
        "enabled": bool(EBAY_CLIENT_ID),
        "type": "api",
        "color": "#9b59b6",
    },
    "openfoodfacts": {
        "name": "Open Food Facts",
        "enabled": True,
        "type": "api",
        "color": "#27ae60",
    },
}

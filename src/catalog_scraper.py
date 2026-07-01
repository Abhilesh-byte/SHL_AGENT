"""
Scrapes the SHL Individual Test Solutions catalog into catalog.json.

WHY THIS IS SEPARATE FROM main.py:
The FastAPI service must answer in under 30 seconds per the assignment spec.
Scraping ~370 product pages live, per request, is far too slow. So we scrape
ONCE, offline, save the result as static JSON, and main.py just loads that
JSON at startup. This script is a build-time tool, not a runtime dependency.

RUN THIS LOCALLY (not in a sandboxed environment) since it needs open
internet access to www.shl.com:

    pip install requests beautifulsoup4
    python catalog_scraper.py

It writes app/catalog.json, overwriting the sample data used for development.
"""
import json
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SHLCatalogBot/1.0)"}

# SHL's catalog page is split into "Pre-packaged Job Solutions" and
# "Individual Test Solutions" tables, each paginated. We only want the
# Individual Test Solutions table (type=1 in SHL's own query params, but
# verify this against the live page since it can change).
INDIVIDUAL_TYPE_PARAM = "type=1"


def get_page(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def parse_test_type_legend(soup: BeautifulSoup) -> dict:
    """
    SHL marks each product row with short type-code badges (K, P, A, B, C, D...).
    The legend explaining what each letter means is usually printed at the
    bottom of the catalog page. Scrape it so your prompt/UI can explain codes
    accurately instead of guessing.
    """
    legend = {}
    # Inspect the live page's HTML to find the actual container — selectors
    # below are illustrative placeholders, adjust after inspecting real markup.
    for row in soup.select(".product-catalogue-legend li"):
        text = row.get_text(strip=True)
        if ":" in text:
            code, meaning = text.split(":", 1)
            legend[code.strip()] = meaning.strip()
    return legend


def parse_catalog_page(soup: BeautifulSoup) -> list[dict]:
    entries = []
    # Placeholder selector — replace with the real row selector after
    # inspecting https://www.shl.com/solutions/products/product-catalog/
    for row in soup.select("table.product-catalogue tr[data-type='Individual']"):
        link_tag = row.select_one("a")
        if not link_tag:
            continue
        name = link_tag.get_text(strip=True)
        url = BASE_URL + link_tag["href"] if link_tag["href"].startswith("/") else link_tag["href"]
        type_codes = [b.get_text(strip=True) for b in row.select(".type-badge")]
        remote = bool(row.select_one(".remote-testing-yes"))
        adaptive = bool(row.select_one(".adaptive-irt-yes"))

        entries.append({
            "name": name,
            "url": url,
            "test_type": type_codes,
            "description": "",  # filled in by fetch_description below
            "duration_minutes": None,
            "remote_testing": remote,
            "adaptive_irt": adaptive,
        })
    return entries


def fetch_description(url: str) -> str:
    """Each product has its own detail page with a fuller description."""
    try:
        soup = get_page(url)
        desc_tag = soup.select_one(".product-description, .description")
        return desc_tag.get_text(strip=True) if desc_tag else ""
    except requests.RequestException:
        return ""


def find_pagination_urls(soup: BeautifulSoup, base: str) -> list[str]:
    pages = set()
    for a in soup.select(".pagination a[href]"):
        pages.add(a["href"] if a["href"].startswith("http") else BASE_URL + a["href"])
    return sorted(pages)


def scrape_all() -> list[dict]:
    all_entries = []
    first_page = get_page(f"{CATALOG_URL}?{INDIVIDUAL_TYPE_PARAM}")
    all_entries.extend(parse_catalog_page(first_page))

    for page_url in find_pagination_urls(first_page, CATALOG_URL):
        soup = get_page(page_url)
        all_entries.extend(parse_catalog_page(soup))
        time.sleep(0.5)  # be polite to SHL's servers

    # De-dupe by URL (pagination overlaps sometimes)
    seen = set()
    deduped = []
    for e in all_entries:
        if e["url"] not in seen:
            seen.add(e["url"])
            deduped.append(e)

    # Enrich each with its full description
    for entry in deduped:
        entry["description"] = fetch_description(entry["url"])
        time.sleep(0.3)

    return deduped


if __name__ == "__main__":
    catalog = scrape_all()
    with open("catalog.json", "w") as f:
        json.dump(catalog, f, indent=2)
    print(f"Scraped {len(catalog)} individual test solutions -> catalog.json")
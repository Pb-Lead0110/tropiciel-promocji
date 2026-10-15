from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

def get_price(url):
    with sync_playwright() as p:
        # Uruchamiamy przeglądarkę Chromium z wyłączoną flagą automatyzacji
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )

        page = context.new_page()

        try:
            # Przechodzimy na stronę i czekamy na wczytanie sieci
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000) # 3 sekundy na wygenerowanie kodu

            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # Metoda 1: Meta OpenGraph
            meta_price = soup.find('meta', attrs={'property': 'product:price:amount'})
            if meta_price and meta_price.get('content'):
                return float(meta_price['content'])

            # Metoda 2: JSON-LD (Schema.org)
            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if item.get("@type") == "Product" and item.get("offers"):
                            offers = item.get("offers")
                            price = offers[0].get("price") if isinstance(offers, list) else offers.get("price")
                            if price is not None:
                                return float(price)
                except:
                    continue

            return None

        except Exception as e:
            print(f"Błąd podczas pobierania strony: {e}")
            return None

        finally:
            browser.close()
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

def get_price(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # WSTRZYKNIĘCIE POLSKIEJ TOŻSAMOŚCI DLA SERWERÓW GITHUBA
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="pl-PL",                   # Wymuszamy polski język
            timezone_id="Europe/Warsaw",      # Wymuszamy polską strefę czasową
            extra_http_headers={
                "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.google.pl/" # Udajemy wejście z polskiego Google
            }
        )
        
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(4000) 

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

            # TRYB DEBUGOWANIA - Jeśli nadal nie znajduje danych, zrób zrzut ekranu
            print("Nie znaleziono ceny. Sprawdzam, czy to blokada Cloudflare...")
            return None

        except Exception as e:
            print(f"Błąd podczas pobierania strony: {e}")
            return None

        finally:
            browser.close()
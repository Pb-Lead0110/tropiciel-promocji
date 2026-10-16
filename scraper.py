from playwright.sync_api import sync_playwright
import re

def get_price(url):
    """
    Pobiera cenę produktu z domeny docelowej (np. Media Expert).
    Wykorzystuje Chromium w trybie headless do obsługi systemów anty-bot (np. Cloudflare)
    oraz poprawnego renderowania dynamicznych elementów DOM.
    """
    with sync_playwright() as p:
        # Inicjalizacja przeglądarki z wyłączonymi flagami automatyzacji
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Konfiguracja kontekstu na profil użytkownika PL w celu minimalizacji ryzyka odrzucenia
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="pl-PL",
            timezone_id="Europe/Warsaw",
            extra_http_headers={
                "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.google.pl/"
            }
        )
        
        page = context.new_page()

        try:
            print(f"Rozpoczęto analizę URL: {url}")
            response = page.goto(url, wait_until="domcontentloaded", timeout=60000)

            print(f"Status HTTP: {response.status if response else 'Brak odpowiedzi sieciowej'}")
            print(f"Tytuł strony: {page.title()}")

            try:
                # Ekstrakcja danych cenowych (złotówki i grosze) bezpośrednio z węzłów tekstowych
                whole = page.locator("span.whole").first
                cents = page.locator("span.cents").first

                if whole.count() > 0:
                    w_text = whole.inner_text()
                    # Obsługa produktów z pełnymi kwotami (brak groszy w interfejsie)
                    c_text = cents.inner_text() if cents.count() > 0 else "00"
                    
                    raw_price = f"{w_text}.{c_text}"
                    print(f"Zidentyfikowano wartość surową: {raw_price}")

                    # Normalizacja ciągu znaków (usunięcie formatowania tysięcy i waluty)
                    clean_price = re.sub(r'[^\d.]', '', raw_price)
                    
                    if clean_price:
                        return float(clean_price)
                        
            except Exception as e:
                print(f"Błąd podczas parsowania struktury DOM: {e}")

            print("Proces zakończony brakiem odczytu - nie zidentyfikowano węzła cenowego.")
            return None

        except Exception as e:
            print(f"Błąd połączenia z serwerem docelowym / Timeout: {e}")
            return None

        finally:
            # Zwolnienie zasobów procesu
            browser.close()
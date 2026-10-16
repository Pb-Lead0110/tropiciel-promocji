from playwright.sync_api import sync_playwright
import re

def get_price(url):
    """
    Pobiera stronę podszywając się pod połączenie sieciowe Chrome,
    omija blokady anty-botowe i wyciąga cenę bezpośrednio z głównego elementu HTML (złotówki + grosze).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
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
            print(f"Pobieranie danych z: {url}")
            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            print("Status HTTP:", response.status if response else "brak odpowiedzi")
            print("URL po załadowaniu:", page.url)
            print("Tytuł strony:", page.title())

            try:
                page.locator("span.whole").first.wait_for(
                    state="visible",
                    timeout=15000
                )
            except Exception:
                print("Nie znaleziono widocznego elementu span.whole")
                print("Fragment tekstu strony:", page.locator("body").inner_text()[:1500])
                page.screenshot(path="debug-page.png", full_page=True)

            # --- SZUKANIE CENY BEZPOŚREDNIO W HTML (ZŁOTÓWKI + GROSZE) ---
            
            # Szukamy głownego kontenera z ceną (zazwyczaj ma klasę "price" lub "price-box")
            # a w nim elementów odpowiedzialnych za całe złotówki ("whole") i resztę ("cents")
            # Ponieważ klasy mogą się minimalnie różnić, szukamy tekstu pasującego do wzorca.

            # Playwright pozwala wyciągnąć wszystkie elementy pasujące do selektora.
            # Szukamy elementu <span> zawierającego klasę "whole" (złotówki) w obrębie kontenera głównej sekcji
            
            try:
                # W Media Expert często cena całkowita jest w <span> z klasą 'whole' 
                # Jeśli w przyszłości zmienią to na np 'main-price', trzeba to zaktualizować.
                whole_element = page.locator("span.whole").first
                cents_element = page.locator("span.cents").first

                if whole_element.count() > 0:
                    whole_text = whole_element.inner_text()
                    cents_text = cents_element.inner_text() if cents_element.count() > 0 else "00"

                    # Łączymy "1 999" i "00"
                    raw_price = f"{whole_text}.{cents_text}"
                    print(f"Znalazłem surową cenę na stronie (HTML): {raw_price}")

                    # Czyszczenie (uniwersalne) z ewentualnych spacji i symboli
                    clean_price = re.sub(r'[^\d.]', '', raw_price)
                    
                    if clean_price:
                         return float(clean_price)
            except Exception as extract_error:
                print(f"Nie udało się wyciągnąć ceny ze znaczników HTML: {extract_error}")

            # Awaryjny odczyt - jeśli powyższe nie znajdzie "span.whole", szukamy jakiegokolwiek kontenera z symbolem zł
            # i bardzo ostrożnie filtrujemy.
            try:
                # Ograniczamy szukanie do sekcji z ceną (np. sekcja boczna obok zdjęć)
                # Omijamy stopkę i nagłówek, żeby nie złapać "Koszty dostawy: 20zł"
                # Wymaga to bardziej ogólnego lokatora, ale z większym rygorem czyszczenia.
                
                # Zamiast skomplikowanych xpathów, pobierzemy tekst całej strony i wyłowimy największą liczbę
                # obok symbolu "zł", ale to mogłoby być niebezpieczne.
                pass # na razie zostawiamy pierwszą metodę
                
            except Exception:
                 pass

            print("Nie znaleziono ceny w kodzie pomimo udanego wczytania strony.")
            return None

        except Exception as e:
            print(f"Błąd podczas pobierania strony: {e}")
            return None

        finally:
            browser.close()
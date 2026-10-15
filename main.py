from database import setup_database, add_product, add_price_log, get_all_products
from scraper import get_price
from datetime import datetime
import time

def main():
    print("Uruchamiam Tropiciela Promocji...")
    setup_database()
    
    # 1. Zdefiniuj produkty do śledzenia
    produkty_do_sledzenia = [
        {"nazwa": "Słuchawki Sony MX5", "url": "https://www.mediaexpert.pl/telewizory-i-rtv/sluchawki/wszystkie-sluchawki/sluchawki-bluetooth-sony-wh1000xm5b-ce7-anc-nauszne-czarne"},
        {"nazwa": "Telewizor LG OLED", "url": "https://www.mediaexpert.pl/telewizory-i-rtv/telewizory/telewizor-lg-55c5elb-55-oled-4k-120hz-webos-dolby-vision-dolby-atmos-hdmi-2-1"}
    ]
    
    # 2. Dodaj je do bazy (jeśli jeszcze ich tam nie ma)
    for prod in produkty_do_sledzenia:
        add_product(prod["nazwa"], prod["url"])
        
    # 3. Pobierz listę produktów z bazy i sprawdź ich ceny
    dzisiaj = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    wszystkie_produkty = get_all_products()
    
    for product_id, url in wszystkie_produkty:
        print(f"Sprawdzam: {url}")
        
        # Scraper zwraca teraz czystą liczbę (float) pobraną z JSON-LD
        cena = get_price(url)
        
        if cena:
            add_price_log(product_id, dzisiaj, cena)
            print(f"Zapisano cenę: {cena} zł")
        else:
            print("Nie udało się pobrać ceny z metadanych na tej stronie.")
            
        # Krótka pauza między zapytaniami dla bezpieczeństwa
        time.sleep(2)
        
    print("Skanowanie zakończone!")

if __name__ == "__main__":
    main()
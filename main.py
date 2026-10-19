from database import setup_database, add_product, add_price_log, get_all_products
from scraper import get_price
from datetime import datetime
import time

def main():
    print("Uruchamiam Tropiciela Promocji...")
    setup_database()
    
    # 1. Zdefiniuj produkty do śledzenia
    produkty_do_sledzenia = [
        {"nazwa": "Słuchawki Sony XM5", "url": "https://www.mediaexpert.pl/telewizory-i-rtv/sluchawki/wszystkie-sluchawki/sluchawki-bluetooth-sony-wh1000xm5b-ce7-anc-nauszne-czarne"},
        {"nazwa": "Telewizor LG OLED 55 cali", "url": "https://www.mediaexpert.pl/telewizory-i-rtv/telewizory/telewizor-lg-55c5elb-55-oled-4k-120hz-webos-dolby-vision-dolby-atmos-hdmi-2-1"},
        {"nazwa": "Smartfon Samsung Galaxy A57", "url": "https://www.mediaexpert.pl/smartfony-i-zegarki/smartfony/smartfon-samsung-galaxy-a57-5g-8-128gb-6-7-120hz-granatowy-sm-a576"},
        {"nazwa": "Ekspress Delonghi Eletta Explore", "url": "https://www.mediaexpert.pl/agd-male/ekspresy-i-kawa/ekspresy-cisnieniowe/ekspres-delonghi-eletta-explore-ecam450-55-g"},
        {"nazwa": "Smartwatch HUAWEI Watch GT 7 Pro Active", "url": "https://www.mediaexpert.pl/smartfony-i-zegarki/smartwatche-i-zegarki/smartwatche/smartwatch-huawei-watch-gt-7-pro-active-46mm-czarny"},
        {"nazwa": "Odkurzacz pionowy BOSCH Unlimited 7", "url": "https://www.mediaexpert.pl/agd-male/sprzatanie/odkurzacze-pionowe/odkurzacz-bosch-unlimited-7-bcs711ext"},
        {"nazwa": "Soundbar JBL BAR 500 MkII", "url": "https://www.mediaexpert.pl/telewizory-i-rtv/kina-domowe/soundbary/soundbar-jbl-bar-500-mkii-czarny-5-1-kanalowy-bezprzewodowy-subwoofer-4k-dolby-vision-hdmi-earc-multibeamtm-3-0-wi-fi"},
        {"nazwa": "Zmywarka BEKO BDIN38542P PowerIntense", "url": "https://www.mediaexpert.pl/agd-do-zabudowy/zmywarki-do-zabudowy/zmywarka-beko-bpro500-bdin38542p"},
        {"nazwa": "Monitor LG UltraGear 27GS75Q-B 27", "url": "https://www.mediaexpert.pl/komputery-i-tablety/monitory-led/monitor-lg-ultragear-27gs75q-b-27-2560x1440px-ips-200hz-1-ms-gtg"},
        {"nazwa": "Laptop LENOVO LOQ 15AHP9 83DX00EYPB 15.6", "url": "https://www.mediaexpert.pl/komputery-i-tablety/laptopy-i-ultrabooki/laptopy/laptop-lenovo-loq-15ahp9-83dx00eypb-15-6-ips-144hz-r7-7445hs-16gb-ram-512gb-ssd-geforce-rtx3050-windows-11-home-funkcje-"}
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
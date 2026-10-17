# Tropiciel Promocji

W pełni zautomatyzowany system w Pythonie do monitorowania cen produktów w sklepie internetowym ("żółto-czarne logo").
Omija zaawansowane zabezpieczenia anty-botowe, korzystając z biblioteki Playwright i wydobywa rzeczywistą cenę bezpośrednio z wyrenderowanych węzłów DOM, symulując zachowanie prawdziwego użytkownika.

# Funkcje
* Precyzyjna ekstrakcja danych: Pobieranie wartości cenowych ze specyficznych znaczników HTML przy użyciu wbudowanych selektorów Playwright
* Omijanie blokad: Wykorzystanie Playwright do radzenia sobie z systemami klasy Cloudflare.
* Lokalna Baza Danych: Trwałe zapisywanie historii cen do lekkiej, relacyjnej bazy SQLite
* Lokalny Harmonogram: Skrypt przystosowany do cyklicznego uruchamiania w tle bezpośrednio z poziomu systemu operacyjnego
* Dashboard Analityczny: Zintegrowany, darmowy panel w Streamlit Cloud do interaktywnej wizualizacji trendów i wahań cen

# Technologie i Narzędzia
* Python 3.11+
* Playwright
* SQLite3
* Pandas
* Streamlit
* Plotly
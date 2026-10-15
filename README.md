# Tropiciel Promocji

W pełni zautomatyzowany skrypt w Pythonie do monitorowania cen produktów w sklepie internetowym "żółto - czarne logo". 
Omija zaawansowane zabezpieczenia anty-botowe, korzystając z biblioteki Playwright, i wydobywa rzeczywistą cenę z ukrytych metadanych (JSON-LD / Open Graph).

# Funkcje
* Pobieranie danych z ustrukturyzowanych tagów Schema.org zamiast zawodnego szukania tekstu w HTML.
*  Wykorzystanie Playwright do radzenia sobie z ochroną przed botami.
*  Zapisywanie historii cen do lokalnej bazy `ceny_tracker.db`.
*  GitHub Actions codziennie automatycznie uruchamia skanowanie o 8:00 rano.
*  Podpięty darmowy panel Streamlit Cloud do wizualizacji spadków i wzrostów cen.

## 🛠️ Technologie
* Python 3.11+
* Playwright
* BeautifulSoup4
* SQLite3
* Pandas
* Streamlit 
* Plotly
* GitHub Actions
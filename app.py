import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# 1. Konfiguracja strony - ciemny motyw (lub jasny w zaleznosci od systemu) i szeroki uklad
st.set_page_config(
    page_title="Tropiciel Promocji", 
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Funkcja do pobierania danych
@st.cache_data(ttl=60) # Odświeżaj dane co minutę, żeby nie zamęczać bazy
def load_data():
    try:
        conn = sqlite3.connect('ceny_tracker.db')
        query = '''
            SELECT p.Name, pl.Check_Date, pl.Current_Price
            FROM Price_Logs pl
            JOIN Products p ON pl.Product_ID = p.Product_ID
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Konwersja kolumny Check_Date z tekstu na prawdziwy format Daty i Czasu
        df['Check_Date'] = pd.to_datetime(df['Check_Date'])
        # Sortowanie od najstarszego wpisu do najnowszego
        df = df.sort_values(by='Check_Date')
        return df
    except sqlite3.OperationalError:
        return pd.DataFrame()

df = load_data()

# 3. Budowa interfejsu (Jeśli są dane)
if not df.empty:
    
    # --- PASEK BOCZNY (SIDEBAR) ---
    st.sidebar.title("⚙️ Filtry")
    produkty_lista = df['Name'].unique().tolist()
    wybrane_produkty = st.sidebar.multiselect(
        "Wybierz produkty do wyświetlenia:", 
        options=produkty_lista, 
        default=produkty_lista # Domyślnie zaznacz wszystko
    )
    
    # Filtrowanie Dataframe na podstawie wyboru w menu bocznym
    filtered_df = df[df['Name'].isin(wybrane_produkty)]
    
    # --- PANEL GŁÓWNY ---
    st.title("🎯 Dashboard: Tropiciel Promocji")
    st.markdown("Automatyczny monitoring cen wybranej elektroniki. Dane aktualizowane codziennie.")
    st.divider() # Estetyczna linia oddzielająca
    
    # --- METRYKI (KPI) NA SAMEJ GÓRZE ---
    st.subheader("Aktualny przegląd sytuacji")
    
    # Dynamiczne tworzenie kolumn w zależności od liczby obserwowanych produktów
    cols = st.columns(len(wybrane_produkty) if len(wybrane_produkty) > 0 else 1)
    
    for idx, produkt in enumerate(wybrane_produkty):
        dane_produktu = filtered_df[filtered_df['Name'] == produkt]
        if not dane_produktu.empty:
            ostatnia_cena = dane_produktu.iloc[-1]['Current_Price']
            
            if len(dane_produktu) > 1:
                poprzednia_cena = dane_produktu.iloc[-2]['Current_Price']
                roznica = ostatnia_cena - poprzednia_cena
            else:
                roznica = 0
                
            # Dynamiczne dobieranie koloru i tekstu
            if roznica < 0:
                kolor = "inverse"  # Spadek ceny: Streamlit pokaże na zielono (ze strzałką w dół)
                tekst = f"-{roznica:.2f} zł"
            elif roznica > 0:
                kolor = "inverse"  # Wzrost ceny: Streamlit pokaże na czerwono (ze strzałką w górę)
                tekst = f"+{roznica:.2f} zł" # Dodajemy plus dla czytelności
            else:
                kolor = "off"      # Brak zmian: Szary kolor
                tekst = "~"
                
            with cols[idx]:
                st.metric(
                    label=produkt, 
                    value=f"{ostatnia_cena:.2f} zł", 
                    delta=tekst,
                    delta_color=kolor
                )
                
    st.divider()

    # --- WYKRES LINIOWY ---
    st.subheader("Wykres wahań cenowych")
    if not filtered_df.empty:
        fig = px.line(
            filtered_df, 
            x='Check_Date', 
            y='Current_Price', 
            color='Name',
            markers=True,
            line_shape="spline", # Łagodne zagięcia wykresu
            labels={'Check_Date': 'Data pomiaru', 'Current_Price': 'Cena (zł)', 'Name': 'Produkt'}
        )
        
        # Estetyka wykresu (m.in. dynamiczna skala Y)
        fig.update_layout(
            yaxis_title="Kwota brutto (PLN)",
            xaxis_title="",
            legend_title="Monitorowane pozycje:",
            hovermode="x unified", # Pokazuje zbiorcze dane po najechaniu myszką
            margin=dict(l=0, r=0, t=30, b=0)
        )
        # Oś Y od razu dopasowuje się do danych, nie startując od zera (lepiej widać piki promocyjne)
        fig.update_yaxes(rangemode="normal") 
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Zaznacz minimum jeden produkt z panelu bocznego, by wyświetlić wykres.")
        
    st.divider()

    # --- TABELA DANYCH (Oczyszczona z indeksów) ---
    st.subheader("Ostatnio zapisane logi")
    
    # Przygotowanie kopii tabeli tylko do wyświetlania
    display_df = filtered_df.copy()
    display_df['Check_Date'] = display_df['Check_Date'].dt.strftime('%Y-%m-%d %H:%M')
    display_df['Current_Price'] = display_df['Current_Price'].apply(lambda x: f"{x:.2f} zł")
    
    # Zmiana nazw kolumn na polskie
    display_df = display_df.rename(columns={
        'Name': 'Nazwa produktu', 
        'Check_Date': 'Data sprawdzenia', 
        'Current_Price': 'Zanotowana cena'
    })
    
    # Wyświetlenie tabeli z hide_index=True, aby ukryć pomieszane liczby po lewej stronie!
    st.dataframe(
        display_df.sort_values(by='Data sprawdzenia', ascending=False).head(15), 
        use_container_width=True,
        hide_index=True 
    )

else:
    # Komunikat, gdy baza istnieje, ale jest pusta lub plik się nie wczytał
    st.warning("Brak logów cenowych w bazie. System pobierze pierwsze ceny przy najbliższym skanowaniu.")
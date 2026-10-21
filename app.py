import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# 1. Konfiguracja strony
st.set_page_config(
    page_title="Tropiciel Promocji", 
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Pomocnicza funkcja do formatowania kwot (np. 1 299,00 zł)
def format_pln(val):
    if pd.isna(val):
        return "-"
    return f"{val:,.2f}".replace(",", " ").replace(".", ",").replace(" ", " ") + " zł"

# 2. Funkcja do pobierania danych
@st.cache_data(ttl=60)
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
        
        df['Check_Date'] = pd.to_datetime(df['Check_Date'])
        df = df.sort_values(by='Check_Date')
        
        # --- ZMIANA: Grupowanie po dniu (zachowanie 1 ostatniego pomiaru z danego dnia) ---
        df['Date_Only'] = df['Check_Date'].dt.date
        df = df.drop_duplicates(subset=['Name', 'Date_Only'], keep='last')
        
        # Ustawienie Check_Date na pełną datę bez czasu
        df['Check_Date'] = pd.to_datetime(df['Date_Only'])
        df = df.drop(columns=['Date_Only'])
        
        return df
    except Exception:
        return pd.DataFrame()

df = load_data()

# 3. Budowa interfejsu
if not df.empty:
    
    # --- PASEK BOCZNY (SIDEBAR) ---
    st.sidebar.title("⚙️ Filtry")
    produkty_lista = df['Name'].unique().tolist()
    wybrane_produkty = st.sidebar.multiselect(
        "Wybierz produkty do wyświetlenia:", 
        options=produkty_lista, 
        default=produkty_lista
    )
    
    filtered_df = df[df['Name'].isin(wybrane_produkty)]
    
    # --- PANEL GŁÓWNY ---
    st.title("🎯 Dashboard: Tropiciel Promocji")
    st.markdown("Automatyczny monitoring cen wybranej elektroniki. Dane aktualizowane codziennie.")
    st.divider()
    
    # --- METRYKI (KPI) NA SAMEJ GÓRZE ---
    st.subheader("📊 Przegląd cen wyznaczonych produktów")
    
    if not wybrane_produkty:
        st.info("Zaznacz co najmniej jeden produkt w panelu bocznym, aby zobaczyć metryki.")
    else:
        for produkt in wybrane_produkty:
            dane_produktu = filtered_df[filtered_df['Name'] == produkt]
            
            if not dane_produktu.empty:
                ostatnia_cena = dane_produktu.iloc[-1]['Current_Price']
                min_cena = dane_produktu['Current_Price'].min()
                max_cena = dane_produktu['Current_Price'].max()
                
                # Znalezienie daty wystąpienia najniższej ceny (tylko data)
                row_min = dane_produktu[dane_produktu['Current_Price'] == min_cena].iloc[-1]
                data_min = row_min['Check_Date'].strftime('%d.%m.%Y')
                
                # Obliczenie różnicy względem poprzedniego dnia
                if len(dane_produktu) > 1:
                    poprzednia_cena = dane_produktu.iloc[-2]['Current_Price']
                    roznica = ostatnia_cena - poprzednia_cena
                else:
                    roznica = 0
                
                if roznica < 0:
                    delta_text = format_pln(roznica)
                    delta_color = "inverse"
                elif roznica > 0:
                    delta_text = f"+{format_pln(roznica)}"
                    delta_color = "inverse"
                else:
                    delta_text = None
                    delta_color = "off"
                
                with st.container(border=True):
                    st.markdown(f"### 🏷️ {produkt}")
                    c1, c2, c3 = st.columns(3)
                    
                    with c1:
                        st.metric(
                            label="Aktualna cena", 
                            value=format_pln(ostatnia_cena), 
                            delta=delta_text,
                            delta_color=delta_color
                        )
                    with c2:
                        st.metric(
                            label="📉 Najniższa cena", 
                            value=format_pln(min_cena),
                            help=f"Data najniższej ceny: {data_min}"
                        )
                    with c3:
                        st.metric(
                            label="📈 Najwyższa cena", 
                            value=format_pln(max_cena)
                        )
                
    st.divider()

    # --- WYKRES LINIOWY ---
    st.subheader("📈 Wykres wahań cenowych")
    if not filtered_df.empty:
        fig = px.line(
            filtered_df, 
            x='Check_Date', 
            y='Current_Price', 
            color='Name',
            markers=True,
            line_shape="spline",
            labels={'Check_Date': 'Data pomiaru', 'Current_Price': 'Cena (zł)', 'Name': 'Produkt'}
        )
        
        fig.update_layout(
            yaxis_title="Cena (PLN)",
            xaxis_title="",
            legend_title="Monitorowane pozycje:",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=80, b=0)
        )
        fig.update_xaxes(tickformat="%d.%m.%Y")
        fig.update_yaxes(rangemode="normal", ticksuffix=" zł") 
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Zaznacz minimum jeden produkt z panelu bocznego, by wyświetlić wykres.")
        
    st.divider()

    # --- TABELA DANYCH ---
    st.subheader("📋 Ostatnio zapisane logi")
    
    display_df = filtered_df.copy()
    # Formatowanie daty na sama datę (bez godziny)
    display_df['Check_Date'] = display_df['Check_Date'].dt.strftime('%d.%m.%Y')
    display_df['Current_Price'] = display_df['Current_Price'].apply(format_pln)
    
    display_df = display_df.rename(columns={
        'Name': 'Nazwa produktu', 
        'Check_Date': 'Data sprawdzenia', 
        'Current_Price': 'Zanotowana cena'
    })
    
    st.dataframe(
        display_df.sort_values(by='Data sprawdzenia', ascending=False).head(15), 
        use_container_width=True,
        hide_index=True 
    )

else:
    st.warning("Brak logów cenowych w bazie. System pobierze pierwsze ceny przy najbliższym skanowaniu.")
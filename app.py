import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tropiciel Promocji", layout="wide")
st.title("📈 Tropiciel Promocji – Historia Cen")

def load_data():
    try:
        conn = sqlite3.connect('ceny_tracker.db')
        query = '''
            SELECT p.Name, pl.Check_Date, pl.Current_Price
            FROM Price_Logs pl
            JOIN Products p ON pl.Product_ID = p.Product_ID
            ORDER BY pl.Check_Date ASC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except sqlite3.OperationalError:
        return pd.DataFrame() # Zwraca pustą tabelę jeśli baza nie istnieje

df = load_data()

if not df.empty:
    fig = px.line(
        df, 
        x='Check_Date', 
        y='Current_Price', 
        color='Name',
        markers=True,
        title="Zmiany cen w czasie (PLN)",
        labels={'Check_Date': 'Data', 'Current_Price': 'Cena (zł)', 'Name': 'Produkt'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Ostatnio zapisane ceny")
    st.dataframe(df.sort_values(by='Check_Date', ascending=False).head(10), use_container_width=True)
else:
    st.warning("Brak danych w bazie. Skrypt musi zapisać pierwsze ceny!")
import sqlite3

DB_NAME = 'ceny_tracker.db'

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabela produktów
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            Product_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            URL TEXT UNIQUE
        )
    ''')
    
    # Tabela historii cen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Price_Logs (
            Log_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Product_ID INTEGER,
            Check_Date DATE,
            Current_Price REAL,
            FOREIGN KEY(Product_ID) REFERENCES Products(Product_ID)
        )
    ''')
    conn.commit()
    conn.close()

def add_product(name, url):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO Products (Name, URL) VALUES (?, ?)", (name, url))
    conn.commit()
    conn.close()

def add_price_log(product_id, date, price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Price_Logs (Product_ID, Check_Date, Current_Price) VALUES (?, ?, ?)", 
                   (product_id, date, price))
    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT Product_ID, URL FROM Products")
    products = cursor.fetchall()
    conn.close()
    return products
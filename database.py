import sqlite3

DB_NAME = "finance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL DEFAULT 'Expense', -- 'Income' atau 'Expense'
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            merchant TEXT,
            date TEXT NOT NULL,
            input_method TEXT NOT NULL,
            image_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_transaction(tx_type, amount, category, merchant, date, input_method, image_path=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (type, amount, category, merchant, date, input_method, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (tx_type, amount, category, merchant, date, input_method, image_path))
    conn.commit()
    conn.close()

def update_transaction(tx_id, tx_type, amount, category, merchant, date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE transactions 
        SET type = ?, amount = ?, category = ?, merchant = ?, date = ?
        WHERE id = ?
    ''', (tx_type, amount, category, merchant, date, tx_id))
    conn.commit()
    conn.close()

def delete_transaction(tx_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ?', (tx_id,))
    conn.commit()
    conn.close()

def get_all_transactions():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, type, amount, category, merchant, date, input_method FROM transactions ORDER BY date DESC, id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows
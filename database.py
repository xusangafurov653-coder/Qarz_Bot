import sqlite3

def init_db():
    conn = sqlite3.connect('qarzlar.db')
    cursor = conn.cursor()
    # Qarzlar jadvalini yaratish
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            kimdan TEXT,
            miqdori TEXT,
            sana TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_debt(user_id, kimdan, miqdori, sana):
    conn = sqlite3.connect('qarzlar.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO debts (user_id, kimdan, miqdori, sana) VALUES (?, ?, ?, ?)',
                   (user_id, kimdan, miqdori, sana))
    conn.commit()
    conn.close()

def get_debts(user_id):
    conn = sqlite3.connect('qarzlar.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, kimdan, miqdori, sana FROM debts WHERE user_id = ?', (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def delete_debt(debt_id):
    conn = sqlite3.connect('qarzlar.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM debts WHERE id = ?', (debt_id,))
    conn.commit()
    conn.close()
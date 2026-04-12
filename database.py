import sqlite3
from werkzeug.security import generate_password_hash

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Создаем таблицы, если их нет
    conn.execute('CREATE TABLE IF NOT EXISTS departments (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS staff 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, dept_id INTEGER, is_active INTEGER DEFAULT 1, 
                    FOREIGN KEY (dept_id) REFERENCES departments (id))''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS results 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_id INTEGER, soft_skills INTEGER, 
                    hard_skills INTEGER, efficiency INTEGER, total_score REAL, verdict TEXT, 
                    date_added TEXT)''')

    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)''')

    # АВТО-МИГРАЦИЯ: Проверяем, есть ли колонка evaluated_by в таблице results
    cursor = conn.execute('PRAGMA table_info(results)')
    columns = [column[1] for column in cursor.fetchall()]
    if 'evaluated_by' not in columns:
        conn.execute('ALTER TABLE results ADD COLUMN evaluated_by INTEGER')
        print("Добавлена колонка evaluated_by")

    # Создаем админа по умолчанию
    try:
        hashed_pw = generate_password_hash('admin', method='pbkdf2:sha256')
        conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', hashed_pw, 'admin'))
    except sqlite3.IntegrityError:
        pass 
    
    conn.commit()
    conn.close()
import sqlite3

# Подключаемся к базе данных (файл casino.db создастся автоматически)
conn = sqlite3.connect('casino.db', check_same_thread=False)
cursor = conn.cursor()

# Создаем таблицу пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        stars INTEGER DEFAULT 50,
        bet INTEGER DEFAULT 10
    )
''')
conn.commit()

def register_user(user_id, username):
    """Регистрирует пользователя или обновляет его юзернейм"""
    clean_username = username.lower().lstrip('@') if username else None
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    if row is None:
        cursor.execute('INSERT INTO users (user_id, username, stars, bet) VALUES (?, ?, 50, 10)', (user_id, clean_username))
    else:
        cursor.execute('UPDATE users SET username = ? WHERE user_id = ?', (clean_username, user_id))
    conn.commit()

def get_stars(user_id):
    """Получает баланс пользователя"""
    cursor.execute('SELECT stars FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if row is None:
        register_user(user_id, None)
        return 50
    return row[0]

def update_stars(user_id, new_balance):
    """Обновляет баланс пользователя"""
    cursor.execute('UPDATE users SET stars = ? WHERE user_id = ?', (max(0, new_balance), user_id))
    conn.commit()

def get_bet(user_id):
    """Получает текущую ставку пользователя"""
    cursor.execute('SELECT bet FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if row is None:
        return 10
    return row[0]

def update_bet(user_id, new_bet):
    """Обновляет ставку пользователя"""
    cursor.execute('UPDATE users SET bet = ? WHERE user_id = ?', (new_bet, user_id))
    conn.commit()

def get_user_id_by_username(username):
    """Ищет user_id по юзернейму"""
    clean_username = username.lower().lstrip('@')
    cursor.execute('SELECT user_id FROM users WHERE username = ?', (clean_username,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return None

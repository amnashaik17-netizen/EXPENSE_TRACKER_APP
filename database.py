import sqlite3

# =============================
# DATABASE CONNECTION
# =============================

conn = sqlite3.connect(
    "expenses.db",
    check_same_thread=False
)

cursor = conn.cursor()

# =============================
# USERS TABLE
# =============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE,

    password BLOB,

    salary REAL DEFAULT 0,

    monthly_budget REAL DEFAULT 0
)
""")

# =============================
# EXPENSES TABLE
# =============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    date TEXT,

    category TEXT,

    amount REAL,

    description TEXT
)
""")

conn.commit()

# =============================
# FUNCTION
# =============================

def get_connection():

    return conn, cursor
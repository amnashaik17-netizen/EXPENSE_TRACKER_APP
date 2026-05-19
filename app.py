import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# =========================
# DATABASE CONNECTION
# =========================

conn = sqlite3.connect("expense_tracker.db", check_same_thread=False)
cursor = conn.cursor()

# =========================
# CREATE USERS TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    salary REAL DEFAULT 0,
    monthly_budget REAL DEFAULT 0
)
""")

# =========================
# ADD MISSING COLUMNS SAFELY
# =========================

try:
    cursor.execute("ALTER TABLE users ADD COLUMN salary REAL DEFAULT 0")
except:
    pass

try:
    cursor.execute("ALTER TABLE users ADD COLUMN monthly_budget REAL DEFAULT 0")
except:
    pass

# =========================
# CREATE EXPENSE TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    amount REAL,
    category TEXT,
    expense_date TEXT
)
""")

conn.commit()

# =========================
# SESSION STATE
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# =========================
# REGISTER FUNCTION
# =========================

def register(username, password):
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return True
    except:
        return False

# =========================
# LOGIN FUNCTION
# =========================

def login(username, password):
    cursor.execute(
        "SELECT id FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()

    if user:
        st.session_state.logged_in = True
        st.session_state.user_id = user[0]
        return True

    return False

# =========================
# SIDEBAR
# =========================

st.sidebar.title("Smart Expense Tracker")

menu = st.sidebar.selectbox(
    "Menu",
    ["Login", "Register"] if not st.session_state.logged_in else ["Dashboard"]
)

# =========================
# REGISTER PAGE
# =========================

if menu == "Register":

    st.title("Register")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Register"):

        if register(new_user, new_pass):
            st.success("Registration Successful")
        else:
            st.error("Username already exists")

# =========================
# LOGIN PAGE
# =========================

elif menu == "Login":

    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if login(username, password):
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Username or Password")

# =========================
# DASHBOARD
# =========================

elif menu == "Dashboard":

    st.title("Expense Tracker Dashboard")

    # LOGOUT
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.rerun()

    # =========================
    # GET USER DATA
    # =========================

    cursor.execute("""
    SELECT salary, monthly_budget
    FROM users
    WHERE id = ?
    """, (st.session_state.user_id,))

    user_data = cursor.fetchone()

    salary = user_data[0]
    monthly_budget = user_data[1]

    st.subheader("Monthly Settings")

    new_salary = st.number_input(
        "Enter Monthly Salary",
        value=float(salary)
    )

    new_budget = st.number_input(
        "Enter Monthly Budget",
        value=float(monthly_budget)
    )

    if st.button("Save Settings"):

        cursor.execute("""
        UPDATE users
        SET salary=?, monthly_budget=?
        WHERE id=?
        """, (
            new_salary,
            new_budget,
            st.session_state.user_id
        ))

        conn.commit()

        st.success("Settings Saved")

    # =========================
    # ADD EXPENSE
    # =========================

    st.subheader("Add Expense")

    title = st.text_input("Expense Title")
    amount = st.number_input("Amount", min_value=0.0)
    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Shopping", "Bills", "Other"]
    )

    if st.button("Add Expense"):

        cursor.execute("""
        INSERT INTO expenses (
            user_id,
            title,
            amount,
            category,
            expense_date
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            st.session_state.user_id,
            title,
            amount,
            category,
            datetime.now().strftime("%Y-%m-%d")
        ))

        conn.commit()

        st.success("Expense Added")

    # =========================
    # SHOW EXPENSES
    # =========================

    st.subheader("Expense History")

    cursor.execute("""
    SELECT title, amount, category, expense_date
    FROM expenses
    WHERE user_id=?
    ORDER BY id DESC
    """, (st.session_state.user_id,))

    data = cursor.fetchall()

    if data:

        df = pd.DataFrame(
            data,
            columns=["Title", "Amount", "Category", "Date"]
        )

        st.dataframe(df)

        total_expense = df["Amount"].sum()

        st.metric("Total Expense", f"₹{total_expense}")

        remaining = monthly_budget - total_expense

        st.metric("Remaining Budget", f"₹{remaining}")

    else:
        st.info("No expenses added yet")
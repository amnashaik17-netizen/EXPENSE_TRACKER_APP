# ==========================================
# ADVANCED EXPENSE TRACKER - FULL APP
# Replace Entire app.py With This Code
# ==========================================

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import hashlib
from datetime import datetime

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Advanced Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #f6f1c7;
}

.main-title {
    font-size: 42px;
    font-weight: bold;
    color: black;
}

.block-container {
    padding-top: 2rem;
}

div.stButton > button {
    background: linear-gradient(to right, #36d1dc, #a445f2);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 25px;
    font-size: 16px;
}

[data-testid="stMetricValue"] {
    font-size: 28px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE CONNECTION
# ==========================================

conn = sqlite3.connect("expense_tracker.db", check_same_thread=False)
c = conn.cursor()

# ==========================================
# CREATE USERS TABLE
# ==========================================

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# ==========================================
# ADD COLUMNS SAFELY
# ==========================================

try:
    c.execute("ALTER TABLE users ADD COLUMN salary REAL DEFAULT 0")
except:
    pass

try:
    c.execute("ALTER TABLE users ADD COLUMN budget REAL DEFAULT 0")
except:
    pass

# ==========================================
# CREATE EXPENSE TABLE
# ==========================================

c.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    date TEXT,
    category TEXT,
    amount REAL,
    description TEXT
)
""")

conn.commit()

# ==========================================
# HASH PASSWORD
# ==========================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================================
# REGISTER USER
# ==========================================

def register_user(username, password):
    try:
        c.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except:
        return False

# ==========================================
# LOGIN USER
# ==========================================

def login_user(username, password):

    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )

    data = c.fetchone()

    return data

# ==========================================
# SESSION STATE
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# LOGIN / REGISTER PAGE
# ==========================================

if not st.session_state.logged_in:

    st.markdown(
        "<div class='main-title'>💰 Advanced Expense Tracker</div>",
        unsafe_allow_html=True
    )

    st.write("")

    option = st.selectbox(
        "Authentication",
        ["Login", "Register"]
    )

    # ======================================
    # LOGIN
    # ======================================

    if option == "Login":

        st.subheader("🔑 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            user = login_user(username, password)

            if user:

                st.success("Login Successful")

                st.session_state.logged_in = True
                st.session_state.username = username

                st.rerun()

            else:
                st.error("Invalid Username or Password")

    # ======================================
    # REGISTER
    # ======================================

    else:

        st.subheader("📝 Register")

        new_username = st.text_input("Create Username")
        new_password = st.text_input(
            "Create Password",
            type="password"
        )

        if st.button("Register"):

            success = register_user(
                new_username,
                new_password
            )

            if success:
                st.success("Account Created Successfully")
            else:
                st.error("Username Already Exists")

# ==========================================
# MAIN APPLICATION
# ==========================================

else:

    username = st.session_state.username

    st.markdown(
        "<div class='main-title'>💰 Advanced Expense Tracker</div>",
        unsafe_allow_html=True
    )

    st.success(f"Logged In User: {username}")

    # ======================================
    # FETCH USER DETAILS
    # ======================================

    c.execute(
        "SELECT salary,budget FROM users WHERE username=?",
        (username,)
    )

    user_data = c.fetchone()

    current_salary = user_data[0]
    current_budget = user_data[1]

    # ======================================
    # FIRST LINE - SALARY
    # ======================================

    st.subheader("💵 Enter Your Salary")

    salary = st.number_input(
        "Monthly Salary",
        min_value=0.0,
        value=float(current_salary),
        step=100.0
    )

    if st.button("Save Salary"):

        c.execute(
            "UPDATE users SET salary=? WHERE username=?",
            (salary, username)
        )

        conn.commit()

        st.success("Salary Saved Successfully")

        st.rerun()

    # ======================================
    # SECOND LINE - BUDGET
    # ======================================

    st.subheader("📌 Enter Your Monthly Budget")

    budget = st.number_input(
        "Monthly Budget",
        min_value=0.0,
        value=float(current_budget),
        step=100.0
    )

    if st.button("Save Budget"):

        c.execute(
            "UPDATE users SET budget=? WHERE username=?",
            (budget, username)
        )

        conn.commit()

        st.success("Budget Saved Successfully")

        st.rerun()

    st.divider()

    # ======================================
    # ADD NEW EXPENSE
    # ======================================

    st.subheader("➕ Add New Expense")

    col1, col2 = st.columns(2)

    with col1:

        expense_date = st.date_input("Date")

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Shopping",
                "Travel",
                "Health",
                "Bills",
                "Education",
                "Other"
            ]
        )

    with col2:

        amount = st.number_input(
            "Amount",
            min_value=0.0
        )

        description = st.text_input("Description")

    if st.button("Save Expense"):

        c.execute("""
        INSERT INTO expenses
        (username,date,category,amount,description)
        VALUES (?,?,?,?,?)
        """, (
            username,
            str(expense_date),
            category,
            amount,
            description
        ))

        conn.commit()

        st.success("Expense Added Successfully")

        st.rerun()

    st.divider()

    # ======================================
    # FETCH USER EXPENSES
    # ======================================

    df = pd.read_sql_query(
        "SELECT * FROM expenses WHERE username=?",
        conn,
        params=(username,)
    )

    # ======================================
    # DASHBOARD METRICS
    # ======================================

    total_expense = (
        df["amount"].sum()
        if not df.empty else 0
    )

    total_transactions = len(df)

    average_expense = (
        df["amount"].mean()
        if not df.empty else 0
    )

    st.subheader("📊 Dashboard")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric(
            "Total Expense",
            f"₹ {total_expense}"
        )

    with m2:
        st.metric(
            "Transactions",
            total_transactions
        )

    with m3:
        st.metric(
            "Average Expense",
            round(average_expense, 2)
        )

    # ======================================
    # MONTHLY BUDGET STATUS
    # ======================================

    if budget > 0:

        st.subheader("💳 Monthly Budget")

        progress = total_expense / budget

        if progress > 1:
            progress = 1.0

        st.progress(progress)

        if total_expense > budget:
            st.error("⚠ Budget Exceeded")
        else:
            st.success("✅ Budget Under Control")

    st.divider()

    # ======================================
    # FILTERS
    # ======================================

    st.subheader("🔍 Filters")

    if not df.empty:

        categories = ["All"] + list(df["category"].unique())

        selected_category = st.selectbox(
            "Filter Category",
            categories
        )

        if selected_category != "All":
            filtered_df = df[
                df["category"] == selected_category
            ]
        else:
            filtered_df = df

    else:
        filtered_df = df

    # ======================================
    # EXPENSE RECORDS
    # ======================================

    st.subheader("📋 Expense Records")

    st.dataframe(filtered_df)

    st.divider()

    # ======================================
    # DELETE EXPENSE
    # ======================================

    st.subheader("🗑 Delete Expense")

    if not df.empty:

        delete_id = st.selectbox(
            "Select Expense ID",
            df["id"]
        )

        if st.button("Delete Expense"):

            c.execute(
                "DELETE FROM expenses WHERE id=?",
                (int(delete_id),)
            )

            conn.commit()

            st.success("Expense Deleted")

            st.rerun()

    st.divider()

    # ======================================
    # EDIT EXPENSE
    # ======================================

    st.subheader("✏ Edit Expense")

    if not df.empty:

        edit_id = st.selectbox(
            "Select Expense ID To Edit",
            df["id"],
            key="edit_expense"
        )

        selected_row = df[df["id"] == edit_id].iloc[0]

        new_category = st.selectbox(
            "New Category",
            [
                "Food",
                "Shopping",
                "Travel",
                "Health",
                "Bills",
                "Education",
                "Other"
            ]
        )

        new_amount = st.number_input(
            "New Amount",
            value=float(selected_row["amount"])
        )

        new_description = st.text_input(
            "New Description",
            value=selected_row["description"]
        )

        if st.button("Update Expense"):

            c.execute("""
            UPDATE expenses
            SET category=?,
                amount=?,
                description=?
            WHERE id=?
            """, (
                new_category,
                new_amount,
                new_description,
                int(edit_id)
            ))

            conn.commit()

            st.success("Expense Updated Successfully")

            st.rerun()

    st.divider()

    # ======================================
    # ANALYTICS
    # ======================================

    st.subheader("📈 Expense Analytics")

    if not df.empty:

        pie_chart = px.pie(
            df,
            names="category",
            values="amount",
            hole=0.5
        )

        st.plotly_chart(
            pie_chart,
            use_container_width=True
        )

        bar_chart = px.bar(
            df,
            x="category",
            y="amount",
            color="category"
        )

        st.plotly_chart(
            bar_chart,
            use_container_width=True
        )

    st.divider()

    # ======================================
    # EXPORT CSV
    # ======================================

    st.subheader("📤 Export Data")

    if not df.empty:

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Export CSV",
            csv,
            file_name="expenses.csv",
            mime="text/csv"
        )

    st.divider()

    # ======================================
    # LOGOUT
    # ======================================

    if st.button("Logout"):

        st.session_state.logged_in = False

        st.rerun()
        c.execute("ALTER TABLE expenses ADD COLUMN username TEXT")
conn.commit()
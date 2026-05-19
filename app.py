import streamlit as st

# =============================
# LOAD CSS
# =============================

def load_css():

    with open("assets/style.css") as f:

        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css()

import pandas as pd
import plotly.express as px
from datetime import datetime
from database import get_connection
from auth import register_user, login_user

# =============================
# PAGE CONFIG
# =============================

st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# =============================
# DATABASE
# =============================

conn, cursor = get_connection()

# =============================
# SESSION STATES
# =============================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False

# =============================
# LOGIN / REGISTER PAGE
# =============================

if not st.session_state.logged_in:

    st.markdown(
        """
        <h1 style='text-align:center;'>
        💰 Smart Expense Tracker
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown("##")

    col1, col2 = st.columns(2)

    # =============================
    # LOGIN
    # =============================

    with col1:

        st.subheader("🔑 Login")

        login_username = st.text_input(
            "Username"
        )

        login_password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            user = login_user(
                login_username,
                login_password
            )

            if user:

                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]

                st.success(
                    "Login Successful!"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid Username or Password"
                )

    # =============================
    # REGISTER
    # =============================

    with col2:

        st.subheader("📝 Register")

        new_username = st.text_input(
            "Create Username"
        )

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

                st.success(
                    "Account Created Successfully!"
                )

            else:

                st.error(
                    "Username Already Exists"
                )

    st.stop()

# =============================
# DASHBOARD
# =============================

st.title(
    f"💰 Welcome {st.session_state.username}"
)

# =============================
# LOGOUT
# =============================

if st.button("Logout"):

    st.session_state.logged_in = False

    st.rerun()

# =============================
# LOAD USER FINANCIAL DATA
# =============================

cursor.execute("""
SELECT salary, monthly_budget
FROM users
WHERE id = ?
""", (st.session_state.user_id,))

user_finance = cursor.fetchone()

saved_salary = user_finance[0]
saved_budget = user_finance[1]

# =============================
# FINANCIAL SETTINGS
# =============================

st.subheader("💵 Monthly Planning")

col1, col2 = st.columns(2)

salary = col1.number_input(
    "Enter Monthly Salary",
    min_value=0.0,
    value=float(saved_salary),
    step=1000.0
)

monthly_budget = col2.number_input(
    "Enter Monthly Budget",
    min_value=0.0,
    value=float(saved_budget),
    step=1000.0
)

if st.button("Save Financial Settings"):

    cursor.execute("""
    UPDATE users
    SET salary = ?,
        monthly_budget = ?
    WHERE id = ?
    """, (
        salary,
        monthly_budget,
        st.session_state.user_id
    ))

    conn.commit()

    st.success(
        "Financial Settings Saved!"
    )

    st.rerun()

# =============================
# ADD EXPENSE
# =============================

st.subheader("➕ Add Expense")

col1, col2, col3 = st.columns(3)

expense_date = col1.date_input(
    "Date"
)

category = col2.selectbox(
    "Category",
    [
        "Food",
        "Travel",
        "Shopping",
        "Bills",
        "Entertainment",
        "Health",
        "Education",
        "Other"
    ]
)

amount = col3.number_input(
    "Amount",
    min_value=0.0,
    step=1.0
)

description = st.text_input(
    "Description"
)

if st.button("Save Expense"):

    cursor.execute("""
    INSERT INTO expenses(
        user_id,
        date,
        category,
        amount,
        description
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        st.session_state.user_id,
        str(expense_date),
        category,
        amount,
        description
    ))

    conn.commit()

    st.success(
        "Expense Added Successfully!"
    )

    st.rerun()

# =============================
# LOAD USER DATA
# =============================

query = f"""
SELECT * FROM expenses
WHERE user_id = {st.session_state.user_id}
"""

df = pd.read_sql_query(
    query,
    conn
)

# =============================
# AUTO EXPORT EXCEL
# =============================

if not df.empty:

    df.to_excel(
        "expenses.xlsx",
        index=False,
        engine="openpyxl"
    )

# =============================
# CALCULATIONS
# =============================

total_expense = 0

if not df.empty:

    total_expense = df["amount"].sum()

remaining_budget = monthly_budget - total_expense

savings = salary - total_expense

average_expense = 0

if len(df) > 0:

    average_expense = total_expense / len(df)

# =============================
# METRICS
# =============================

st.subheader("📊 Financial Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💵 Total Expense",
    f"₹ {round(total_expense,2)}"
)

col2.metric(
    "💰 Remaining Budget",
    f"₹ {round(remaining_budget,2)}"
)

col3.metric(
    "🏦 Savings",
    f"₹ {round(savings,2)}"
)

col4.metric(
    "📈 Average Expense",
    f"₹ {round(average_expense,2)}"
)

# =============================
# BUDGET ALERT
# =============================

progress = 0

if monthly_budget > 0:

    progress = min(
        total_expense / monthly_budget,
        1.0
    )

st.progress(progress)

if total_expense > monthly_budget:

    st.error(
        "⚠ Budget Limit Exceeded!"
    )

else:

    st.success(
        "✅ Budget Under Control"
    )

# =============================
# SEARCH
# =============================

st.subheader("🔍 Search Expenses")

search = st.text_input(
    "Search By Category"
)

filtered_df = df.copy()

if search != "":

    filtered_df = filtered_df[
        filtered_df["category"].str.contains(
            search,
            case=False
        )
    ]

# =============================
# SHOW TABLE
# =============================

st.subheader("📋 Expense Records")

st.dataframe(
    filtered_df,
    use_container_width=True
)

# =============================
# DELETE EXPENSE
# =============================

st.subheader("🗑 Delete Expense")

if not filtered_df.empty:

    expense_ids = filtered_df["id"].tolist()

    selected_id = st.selectbox(
        "Select Expense ID",
        expense_ids
    )

    if st.button("Delete Expense"):

        cursor.execute("""
        DELETE FROM expenses
        WHERE id = ?
        """, (selected_id,))

        conn.commit()

        st.success(
            "Expense Deleted Successfully!"
        )

        st.rerun()

# =============================
# EDIT EXPENSE
# =============================

st.subheader("✏ Edit Expense")

if not filtered_df.empty:

    edit_id = st.selectbox(
        "Select Expense ID To Edit",
        expense_ids
    )

    selected_row = filtered_df[
        filtered_df["id"] == edit_id
    ].iloc[0]

    new_category = st.selectbox(
        "New Category",
        [
            "Food",
            "Travel",
            "Shopping",
            "Bills",
            "Entertainment",
            "Health",
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

        cursor.execute("""
        UPDATE expenses
        SET category = ?,
            amount = ?,
            description = ?
        WHERE id = ?
        """, (
            new_category,
            new_amount,
            new_description,
            edit_id
        ))

        conn.commit()

        st.success(
            "Expense Updated Successfully!"
        )

        st.rerun()

# =============================
# CHARTS
# =============================

if not filtered_df.empty:

    st.subheader("📈 Expense Analytics")

    category_data = filtered_df.groupby(
        "category"
    )["amount"].sum().reset_index()

    pie_chart = px.pie(
        category_data,
        names="category",
        values="amount",
        hole=0.4,
        title="Category Distribution"
    )

    st.plotly_chart(
        pie_chart,
        use_container_width=True
    )

    bar_chart = px.bar(
        category_data,
        x="category",
        y="amount",
        color="category",
        title="Expenses By Category"
    )

    st.plotly_chart(
        bar_chart,
        use_container_width=True
    )

    filtered_df["date"] = pd.to_datetime(
        filtered_df["date"]
    )

    daily_data = filtered_df.groupby(
        "date"
    )["amount"].sum().reset_index()

    line_chart = px.line(
        daily_data,
        x="date",
        y="amount",
        markers=True,
        title="Daily Expense Trend"
    )

    st.plotly_chart(
        line_chart,
        use_container_width=True
    )

# =============================
# DOWNLOAD EXCEL
# =============================

st.subheader("📥 Download Excel Report")

if not df.empty:

    with open("expenses.xlsx", "rb") as file:

        st.download_button(
            label="⬇ Download Excel File",
            data=file,
            file_name="expenses.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# =============================
# FOOTER
# =============================

st.markdown("---")

st.markdown(
    """
    <center>
    <h4>
    Developed with ❤️ using Streamlit
    </h4>
    </center>
    """,
    unsafe_allow_html=True
)
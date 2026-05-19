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
from auth import authentication_page
# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# ---------------- DATABASE ----------------
conn, cursor = get_connection()

# ---------------- TITLE ----------------
st.title("💰 Advanced Expense Tracker")

# ---------------- AUTH ----------------
authentication_page()

if "logged_in" not in st.session_state:

    st.warning("Please Login First")
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.title("➕ Add New Expense")

expense_date = st.sidebar.date_input("Date")

category = st.sidebar.selectbox(
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

amount = st.sidebar.number_input(
    "Amount",
    min_value=0.0,
    step=1.0
)

description = st.sidebar.text_input(
    "Description"
)

# ---------------- SAVE EXPENSE ----------------
if st.sidebar.button("Save Expense"):

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
        st.session_state["user_id"],
        str(expense_date),
        category,
        amount,
        description
    ))

    conn.commit()

    st.sidebar.success(
        "Expense Added Successfully!"
    )

# ---------------- LOAD DATA ----------------
query = f"""
SELECT * FROM expenses
WHERE user_id = {st.session_state["user_id"]}
"""

df = pd.read_sql_query(query, conn)

# ---------------- DASHBOARD METRICS ----------------
total_expense = 0

if not df.empty:

    total_expense = df["amount"].sum()

total_transactions = len(df)

average_expense = 0

if total_transactions > 0:

    average_expense = total_expense / total_transactions

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "💵 Total Expenses",
    f"₹ {round(total_expense, 2)}"
)

col2.metric(
    "📌 Transactions",
    total_transactions
)

col3.metric(
    "📈 Average Expense",
    f"₹ {round(average_expense, 2)}"
)

# ---------------- BUDGET ALERT ----------------
monthly_budget = 10000

progress = min(total_expense / monthly_budget, 1.0)

st.subheader("💳 Monthly Budget")

st.progress(progress)

if total_expense > monthly_budget:

    st.error("⚠ Budget Limit Exceeded!")

else:

    st.success("✅ Budget Under Control")

# ---------------- FILTERS ----------------
st.subheader("🔍 Filters")

col1, col2 = st.columns(2)

search = col1.text_input(
    "Search Category"
)

selected_category = col2.selectbox(
    "Filter Category",
    [
        "All",
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

# ---------------- APPLY FILTERS ----------------
filtered_df = df.copy()

if search != "":

    filtered_df = filtered_df[
        filtered_df["category"].str.contains(
            search,
            case=False
        )
    ]

if selected_category != "All":

    filtered_df = filtered_df[
        filtered_df["category"] == selected_category
    ]

# ---------------- SHOW TABLE ----------------
st.subheader("📋 Expense Records")

st.dataframe(
    filtered_df,
    use_container_width=True
)

# ---------------- DELETE EXPENSE ----------------
st.subheader("🗑 Delete Expense")

if not filtered_df.empty:

    expense_ids = filtered_df["id"].tolist()

    selected_id = st.selectbox(
        "Select Expense ID To Delete",
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

# ---------------- EDIT EXPENSE ----------------
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

# ---------------- CHARTS ----------------
if not filtered_df.empty:

    st.subheader("📊 Expense Analytics")

    category_data = filtered_df.groupby(
        "category"
    )["amount"].sum().reset_index()

    # ---------------- PIE CHART ----------------
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

    # ---------------- BAR CHART ----------------
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

    # ---------------- LINE CHART ----------------
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

# ---------------- CSV UPLOAD ----------------
st.subheader("📂 Upload CSV")

uploaded_file = st.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

if uploaded_file is not None:

    upload_df = pd.read_csv(
        uploaded_file
    )

    st.dataframe(
        upload_df,
        use_container_width=True
    )

# ---------------- EXPORT ----------------
st.subheader("📥 Export Data")

if st.button("Export To Excel"):

    file_name = f"expense_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    filtered_df.to_excel(
        file_name,
        index=False,
        engine="openpyxl"
    )

    with open(file_name, "rb") as file:

        st.download_button(
            label="⬇ Download Excel File",
            data=file,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ---------------- FOOTER ----------------
st.markdown("---")

st.markdown(
    f"""
### 👤 Logged In User:
**{st.session_state["username"]}**
"""
)
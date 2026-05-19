import streamlit as st
import bcrypt
from database import get_connection

conn, cursor = get_connection()

# ---------------- HASH PASSWORD ----------------
def hash_password(password):

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

# ---------------- VERIFY PASSWORD ----------------
def verify_password(password, hashed_password):

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password
    )

# ---------------- REGISTER USER ----------------
def register_user(username, password):

    hashed_password = hash_password(password)

    try:

        cursor.execute("""
        INSERT INTO users(username, password)
        VALUES (?, ?)
        """, (
            username,
            hashed_password
        ))

        conn.commit()

        return True

    except:

        return False

# ---------------- LOGIN USER ----------------
def login_user(username, password):

    cursor.execute("""
    SELECT * FROM users
    WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    if user:

        stored_password = user[2]

        if verify_password(password, stored_password):

            return user

    return None

# ---------------- AUTH PAGE ----------------
def authentication_page():

    st.sidebar.title("🔐 Authentication")

    menu = st.sidebar.selectbox(
        "Select Option",
        ["Login", "Register"]
    )

    # ---------------- REGISTER ----------------
    if menu == "Register":

        st.subheader("📝 Create Account")

        new_user = st.text_input("Username")

        new_password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Register"):

            if new_user == "" or new_password == "":

                st.warning("Please Fill All Fields")

            else:

                success = register_user(
                    new_user,
                    new_password
                )

                if success:

                    st.success("Account Created Successfully!")

                else:

                    st.error("Username Already Exists")

    # ---------------- LOGIN ----------------
    elif menu == "Login":

        st.subheader("🔑 Login")

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            user = login_user(
                username,
                password
            )

            if user:

                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user[0]
                st.session_state["username"] = user[1]

                st.success(
                    f"Welcome {user[1]}"
                )

            else:

                st.error(
                    "Invalid Username or Password"
                )
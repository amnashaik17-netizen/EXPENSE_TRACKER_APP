import bcrypt
from database import get_connection

conn, cursor = get_connection()

# =============================
# HASH PASSWORD
# =============================

def hash_password(password):

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

# =============================
# VERIFY PASSWORD
# =============================

def verify_password(password, hashed_password):

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password
    )

# =============================
# REGISTER USER
# =============================

def register_user(username, password):

    hashed_password = hash_password(password)

    try:

        cursor.execute("""
        INSERT INTO users(
            username,
            password
        )
        VALUES (?, ?)
        """, (
            username,
            hashed_password
        ))

        conn.commit()

        return True

    except:

        return False

# =============================
# LOGIN USER
# =============================

def login_user(username, password):

    cursor.execute("""
    SELECT *
    FROM users
    WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    if user:

        stored_password = user[2]

        if verify_password(
            password,
            stored_password
        ):

            return user

    return None
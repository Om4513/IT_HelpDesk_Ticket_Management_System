import streamlit as st
import sqlite3
import pandas as pd
import bcrypt

DB_NAME = "database.db"


# ---------------- DATABASE ----------------
def get_connection():
    return sqlite3.connect(DB_NAME)


# ---------------- PASSWORD ----------------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)


# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.user_id = None


# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="IT Helpdesk Pro", page_icon="🛠️", layout="wide")
st.title("🛠️ IT Helpdesk Management System")
st.markdown("---")


# =========================================================
# ================= AUTH SECTION ==========================
# =========================================================

if not st.session_state.logged_in:

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    # ---------------- LOGIN ----------------
    with tab1:
        st.subheader("Login")

        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT user_id, password, role FROM users WHERE username=?",
                (username,)
            )

            user = cursor.fetchone()
            conn.close()

            if user:
                user_id, stored_password, role = user
                if verify_password(password, stored_password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.session_state.user_id = user_id
                    st.success("Login Successful")
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
            else:
                st.error("User Not Found")

    # ---------------- REGISTER ----------------
    with tab2:
        st.subheader("Register New User")

        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        role = st.selectbox("Role", ["Employee", "Admin"])

        if st.button("Register"):
            if not new_user or not new_pass:
                st.warning("All fields required")
            else:
                hashed = hash_password(new_pass)

                conn = get_connection()
                cursor = conn.cursor()

                try:
                    cursor.execute(
                        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                        (new_user, hashed, role)
                    )
                    conn.commit()
                    st.success("User Registered Successfully")
                except sqlite3.IntegrityError:
                    st.error("Username already exists")
                finally:
                    conn.close()

# =========================================================
# ================= AFTER LOGIN ===========================
# =========================================================

else:
    st.success(f"Welcome {st.session_state.username} ({st.session_state.role})")

    # =====================================================
    # ================= EMPLOYEE PANEL ====================
    # =====================================================

    if st.session_state.role == "Employee":

        menu = st.sidebar.radio(
            "Employee Menu",
            ["Raise Ticket", "View My Tickets", "Logout"]
        )

        if menu == "Raise Ticket":
            st.subheader("🎫 Raise Ticket")

            category = st.selectbox("Category", ["Hardware", "Software", "Network"])
            description = st.text_area("Description")
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])

            if st.button("Submit Ticket"):
                if description.strip() == "":
                    st.warning("Description required")
                else:
                    conn = get_connection()
                    cursor = conn.cursor()

                    cursor.execute("""
                        INSERT INTO tickets (user_id, category, description, priority, status)
                        VALUES (?, ?, ?, ?, 'Open')
                    """, (
                        st.session_state.user_id,
                        category,
                        description,
                        priority
                    ))

                    conn.commit()
                    conn.close()
                    st.success("Ticket Created Successfully")

        elif menu == "View My Tickets":
            st.subheader("📋 My Tickets")

            conn = get_connection()
            df = pd.read_sql_query("""
                SELECT ticket_id, category, description, priority, status
                FROM tickets WHERE user_id=?
            """, conn, params=(st.session_state.user_id,))
            conn.close()

            if df.empty:
                st.info("No Tickets Found")
            else:
                st.dataframe(df, use_container_width=True)

        elif menu == "Logout":
            st.session_state.clear()
            st.rerun()

    # =====================================================
    # ================= ADMIN PANEL =======================
    # =====================================================

    else:

        menu = st.sidebar.radio(
            "Admin Menu",
            ["View All Tickets", "Update Status", "Statistics", "Export CSV", "Logout"]
        )

        if menu == "View All Tickets":
            st.subheader("📊 All Tickets")

            conn = get_connection()
            df = pd.read_sql_query("SELECT * FROM tickets", conn)
            conn.close()

            if df.empty:
                st.info("No Tickets Available")
            else:
                st.dataframe(df, use_container_width=True)

        elif menu == "Update Status":
            st.subheader("🔄 Update Ticket Status")

            ticket_id = st.number_input("Ticket ID", min_value=1)
            new_status = st.selectbox("New Status", ["Open", "In Progress", "Closed"])

            if st.button("Update"):
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    "UPDATE tickets SET status=? WHERE ticket_id=?",
                    (new_status, ticket_id)
                )

                conn.commit()

                if cursor.rowcount == 0:
                    st.error("Ticket Not Found")
                else:
                    st.success("Ticket Updated")

                conn.close()

        elif menu == "Statistics":
            st.subheader("📈 Ticket Statistics")

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM tickets")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM tickets WHERE status='Open'")
            open_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM tickets WHERE status='In Progress'")
            progress_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM tickets WHERE status='Closed'")
            closed_count = cursor.fetchone()[0]

            conn.close()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total", total)
            col2.metric("Open", open_count)
            col3.metric("In Progress", progress_count)
            col4.metric("Closed", closed_count)

        elif menu == "Export CSV":
            st.subheader("⬇ Export Tickets")

            conn = get_connection()
            df = pd.read_sql_query("SELECT * FROM tickets", conn)
            conn.close()

            if df.empty:
                st.warning("No Data Available")
            else:
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Report",
                    csv,
                    "tickets_report.csv",
                    "text/csv"
                )

        elif menu == "Logout":
            st.session_state.clear()
            st.rerun()

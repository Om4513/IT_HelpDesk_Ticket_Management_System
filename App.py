import sqlite3
import csv
import bcrypt
import re
from datetime import datetime

DB_NAME = "database.db"
REPORT_FILE = "tickets_report.csv"
LOG_FILE = "audit_log.txt"


# ================= LOGGING =================

def write_log(action, username="System"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] | User: {username} | Action: {action}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(log_entry)


# ================= DATABASE =================

def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password BLOB NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'Open',
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    conn.commit()
    conn.close()


# ================= VALIDATION =================

def validate_username(username):
    return len(username) >= 4 and username.isalnum() and " " not in username


def validate_password(password):
    return (
        len(password) >= 6
        and re.search(r"[A-Za-z]", password)
        and re.search(r"\d", password)
    )


def validate_priority(priority):
    return priority in ("Low", "Medium", "High")


def validate_status(status):
    return status in ("Open", "In Progress", "Closed")


def ticket_exists(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ticket_id FROM tickets WHERE ticket_id=?", (ticket_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


# ================= SECURITY =================

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)


# ================= REGISTER =================

def register_user():
    print("\n=== User Registration ===")

    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    role = input("Enter role (Employee/Admin): ").strip().capitalize()

    if not validate_username(username):
        print("❌ Username must be 4+ characters, no spaces, alphanumeric only.")
        return

    if not validate_password(password):
        print("❌ Password must be 6+ characters and contain letters & numbers.")
        return

    if role not in ("Employee", "Admin"):
        print("❌ Role must be Employee or Admin.")
        return

    hashed = hash_password(password)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed, role)
        )

        conn.commit()
        print("✅ User registered securely!")
        write_log("User Registered", username)

    except sqlite3.IntegrityError:
        print("❌ Username already exists.")
    except Exception as e:
        print("❌ Registration error:", e)
    finally:
        conn.close()


# ================= LOGIN =================

def login_user():
    print("\n=== User Login ===")

    username = input("Username: ").strip()
    password = input("Password: ").strip()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT user_id, password, role FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()
        conn.close()

        if not user:
            print("❌ Invalid credentials.")
            write_log("Failed Login Attempt", username)
            return

        user_id, stored_password, role = user

        if verify_password(password, stored_password):
            print(f"\n✅ Login successful! Role: {role}")
            write_log("Successful Login", username)

            if role == "Employee":
                employee_menu(user_id, username)
            else:
                admin_menu(username)
        else:
            print("❌ Invalid credentials.")
            write_log("Failed Login Attempt", username)

    except Exception as e:
        print("❌ Login error:", e)


# ================= TICKET FUNCTIONS =================

def raise_ticket(user_id, username):
    print("\n=== Raise Ticket ===")

    category = input("Category (Software/Hardware/Network): ").strip()
    description = input("Description: ").strip()
    priority = input("Priority (Low/Medium/High): ").strip().capitalize()

    if not category or not description:
        print("❌ Fields cannot be empty.")
        return

    if not validate_priority(priority):
        print("❌ Invalid priority.")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tickets (user_id, category, description, priority)
            VALUES (?, ?, ?, ?)
        """, (user_id, category, description, priority))

        conn.commit()
        print("✅ Ticket created successfully!")
        write_log("Ticket Created", username)

    except Exception as e:
        print("❌ Ticket creation error:", e)
    finally:
        conn.close()


def view_my_tickets(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ticket_id, category, description, priority, status
            FROM tickets WHERE user_id=?
        """, (user_id,))

        tickets = cursor.fetchall()
        conn.close()

        if not tickets:
            print("❌ No tickets found.")
            return

        print("\n--- My Tickets ---")
        for ticket in tickets:
            print(f"ID: {ticket[0]} | Category: {ticket[1]}")
            print(f"Priority: {ticket[3]} | Status: {ticket[4]}")
            print(f"Description: {ticket[2]}")
            print("-" * 40)

    except Exception as e:
        print("❌ Error retrieving tickets:", e)


def view_all_tickets():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tickets")
        tickets = cursor.fetchall()
        conn.close()

        if not tickets:
            print("❌ No tickets available.")
            return

        print("\n--- All Tickets ---")
        for ticket in tickets:
            print(f"Ticket ID: {ticket[0]} | User ID: {ticket[1]}")
            print(f"Category: {ticket[2]} | Priority: {ticket[4]} | Status: {ticket[5]}")
            print(f"Description: {ticket[3]}")
            print("-" * 40)

    except Exception as e:
        print("❌ Error retrieving tickets:", e)


def update_ticket_status(username):
    ticket_id = input("Enter Ticket ID: ").strip()

    if not ticket_id.isdigit():
        print("❌ Ticket ID must be numeric.")
        return

    ticket_id = int(ticket_id)

    if not ticket_exists(ticket_id):
        print("❌ Ticket does not exist.")
        return

    new_status = input("New Status (Open/In Progress/Closed): ").strip()

    if not validate_status(new_status):
        print("❌ Invalid status.")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE tickets SET status=? WHERE ticket_id=?",
            (new_status, ticket_id)
        )

        conn.commit()
        print("✅ Status updated successfully!")
        write_log(f"Updated Ticket {ticket_id} to {new_status}", username)

    except Exception as e:
        print("❌ Update error:", e)
    finally:
        conn.close()


def view_ticket_statistics():
    try:
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

        print("\n===== Ticket Statistics =====")
        print(f"Total Tickets : {total}")
        print(f"Open          : {open_count}")
        print(f"In Progress   : {progress_count}")
        print(f"Closed        : {closed_count}")

    except Exception as e:
        print("❌ Statistics error:", e)


def export_tickets_to_csv(username):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets")
        tickets = cursor.fetchall()
        conn.close()

        if not tickets:
            print("❌ No tickets to export.")
            return

        with open(REPORT_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Ticket ID", "User ID", "Category", "Description", "Priority", "Status"])
            writer.writerows(tickets)

        print(f"✅ Tickets exported to {REPORT_FILE}")
        write_log("Exported Tickets to CSV", username)

    except PermissionError:
        print("❌ Close tickets_report.csv before exporting.")
    except Exception as e:
        print("❌ Export error:", e)


# ================= MENUS =================

def employee_menu(user_id, username):
    while True:
        print("\n--- Employee Menu ---")
        print("1. Raise Ticket")
        print("2. View My Tickets")
        print("3. Logout")

        choice = input("Choose: ").strip()

        if choice == "1":
            raise_ticket(user_id, username)
        elif choice == "2":
            view_my_tickets(user_id)
        elif choice == "3":
            write_log("Employee Logout", username)
            print("👋 Logged out.")
            break
        else:
            print("❌ Invalid choice.")


def admin_menu(username):
    while True:
        print("\n--- Admin Menu ---")
        print("1. View All Tickets")
        print("2. Update Ticket Status")
        print("3. View Ticket Statistics")
        print("4. Export Tickets to CSV")
        print("5. Logout")

        choice = input("Choose: ").strip()

        if choice == "1":
            view_all_tickets()
        elif choice == "2":
            update_ticket_status(username)
        elif choice == "3":
            view_ticket_statistics()
        elif choice == "4":
            export_tickets_to_csv(username)
        elif choice == "5":
            write_log("Admin Logout", username)
            print("👋 Logged out.")
            break
        else:
            print("❌ Invalid choice.")


# ================= MAIN =================

def main():
    initialize_database()

    while True:
        print("\n====== IT Helpdesk System ======")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Select option: ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            login_user()
        elif choice == "3":
            write_log("System Exit")
            print("👋 Exiting system.")
            break
        else:
            print("❌ Invalid option.")


if __name__ == "__main__":
    main()

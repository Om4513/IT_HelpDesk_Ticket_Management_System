import sqlite3

# Connect or create the database file
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create the 'users' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Employee', 'Admin'))
);
""")

# Create the 'tickets' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category TEXT,
    description TEXT,
    status TEXT DEFAULT 'Open',
    assigned_to TEXT,
    priority TEXT DEFAULT 'Medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
""")

print("✅ Database and tables created successfully!")

conn.commit()
conn.close()

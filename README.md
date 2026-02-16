🛠 IT Helpdesk Ticket Management System:-

A role-based IT Helpdesk Management System built using Python, SQLite, CLI, and Streamlit.
The project simulates real-world IT support workflows including user authentication, ticket management, reporting, and audit logging.

📌 Project Overview:

This system allows:

👤 User Registration & Login (Employee / Admin)

🎫 Ticket Creation & Tracking

🔄 Ticket Status Updates (Open, In Progress, Closed)

📊 Ticket Export to CSV Report

🔐 Secure Password Hashing using bcrypt

📝 Audit Logging of All Activities

🌐 Web Interface using Streamlit

💻 CLI-Based Application Version


🧰 Tech Stack:

Python 3

SQLite Database

CLI(Terminal Interface via PyCharm)

bcrypt (Password Hashing)

Streamlit (Web Interface)

CSV Module (Report Generation)

📂 Project Structure:

IT_HelpDesk_Ticket_Management_System/

├── App.py                # CLI-based application

├── web_app.py            # Streamlit web application

├── db_setup.py           # Database setup

├── check_users.py        # View users in DB

├── check_tables.py       # Verify DB tables

├── check_sqlite.py       # DB test connection

├── sample_outputs/       # Sample generated reports

├── .gitignore

└── README.md

🔧 Install Dependencies:

⚠ If using Python 3.13 (recommended safe method):

python -m pip install streamlit bcrypt


If needed, upgrade pip first:

python -m pip install --upgrade pip

🗄 Setup Database (First Time Only)

Run:

python db_setup.py


This creates the required SQLite database and tables.

💻 Run CLI Version:

python App.py


Features available in CLI:

Register

Login

Create Ticket

View Tickets

Update Ticket Status

Export CSV

Admin Controls:

🌐 Run Web Version (Streamlit)

⚠ Do NOT run:

python web_app.py


✔ Correct method:

python -m streamlit run web_app.py


Then open your browser:

http://localhost:8501

🔐 Security Implementation

Passwords are securely hashed using bcrypt

Plain text passwords are never stored

Role-based Access Control (Admin / Employee)

All actions recorded in audit_log.txt

📊 Sample Output

Sample generated CSV reports are stored inside:

sample_outputs/ sample_tickets_report.CSV


These demonstrate exported ticket data.

🚀 Key Features Implemented

Secure Authentication System

Role-Based Authorization

CRUD Operations on Tickets

Audit Logging System

CSV Report Generation

CLI + Modern Web Interface

GitHub Project Structure with Proper .gitignore

🎯 Future Enhancements

Cloud Deployment (AWS / Azure)

Email Notifications

Dashboard Analytics

REST API Integration

Docker Containerization

👨‍💻 Author

Om Babar

IT Support / Cloud Enthusiast / Cybersecurity Analyst

Python Developer

⭐ Conclusion

This project demonstrates the practical implementation of:

Database Management

Authentication & Security

Role-Based Access Control

Real IT Workflow Simulation

CLI & Web Application Development


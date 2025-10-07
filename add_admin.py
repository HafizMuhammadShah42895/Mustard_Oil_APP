import mysql.connector
from werkzeug.security import generate_password_hash

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='muhammad@555',
    database='e-commerce'
)
cursor = conn.cursor()

# Admin details
username = input("Enter username:")
password = input("Enter password: ")

# Hash password
hashed_password = generate_password_hash(password)

# Insert admin
cursor.execute(
    "INSERT INTO admin (username,  password_hash) VALUES (%s,%s)",
    (username,hashed_password)
)

conn.commit()
conn.close()
print(f"Admin '{username}' added successfully!")
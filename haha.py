import sqlite3

# Connect to SQLite database (creates a new file or connects to existing one)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

def list_tables():
    """
    Lists all table names in the SQLite database.
    """
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table[0])

# Call the function to list tables
list_tables()

# Close the da
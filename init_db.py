import sqlite3

def create_database():
    conn = sqlite3.connect('order_tracking.db') # This will create the database file
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS order_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position INTEGER NOT NULL,
    date_checked TEXT NOT NULL,
    predict_complete TEXT)''')

    # Save the changes
    conn.commit()

    # Close the connection
    conn.close()

if __name__ == '__main__':
    create_database()
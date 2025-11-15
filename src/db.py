# This module handles all database creation and setup.
# We use Python's built-in sqlite3, so no extra servers are needed.

import sqlite3
from sqlite3 import Error
from config.config import DB_PATH  # Import the database path from our config file


def create_database():
    """
    Creates the SQLite database and the required tables if they don't exist.
    'students' table: Stores student information.
    'attendance' table: Stores a log of every time a student is marked present.
    """

    # SQL commands to create the tables.
    # 'IF NOT EXISTS' is important so we don't overwrite tables.
    create_students_table = """
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        name TEXT NOT NULL
    );
    """

    create_attendance_table = """
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        name TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students (student_id)
    );
    """

    conn = None  # Initialize connection variable
    try:
        # Create a database connection.
        # If the file (students.db) doesn't exist, sqlite3 will create it.
        conn = sqlite3.connect(str(DB_PATH))
        print(f"Connected to database at {DB_PATH}")

        # Create a cursor object to execute SQL commands
        c = conn.cursor()

        # Execute the SQL commands
        c.execute(create_students_table)
        c.execute(create_attendance_table)

        # Commit the changes to the database
        conn.commit()
        print("Tables 'students' and 'attendance' created successfully.")

    except Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Always close the connection, even if an error occurred.
        if conn:
            conn.close()
            print("Database connection closed.")


# This block allows you to run this file directly to create the database.
# e.g., 'python src/db.py'
if __name__ == "__main__":
    create_database()

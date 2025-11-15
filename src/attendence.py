# This is your task, Coder 1.
# This module handles marking attendance in the database.
# It includes the "cooldown" logic to prevent duplicate entries.

import sqlite3
from datetime import datetime
from config.config import DB_PATH, ATTENDANCE_COOLDOWN_SECONDS


def mark_attendance(student_id, name):
    """
    Marks attendance for a given student_id.
    Includes a cooldown to prevent marking the same student multiple times
    in a short period (e.g., every frame).
    """

    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        current_time = datetime.now()
        current_timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # --- 1. Check for cooldown ---
        # Get the timestamp of the *last* time this student was marked.
        c.execute(
            "SELECT timestamp FROM attendance WHERE student_id = ? ORDER BY timestamp DESC LIMIT 1",
            (student_id,),
        )

        last_entry = c.fetchone()  # Gets the most recent row, or None

        if last_entry:
            # If a record exists, check the time difference
            last_timestamp_str = last_entry[0]
            last_timestamp = datetime.strptime(last_timestamp_str, "%Y-%m-%d %H:%M:%S")

            time_diff_seconds = (current_time - last_timestamp).total_seconds()

            # If it's been less than the cooldown period, do nothing.
            if time_diff_seconds < ATTENDANCE_COOLDOWN_SECONDS:
                # print(f"Cooldown active for {name}. Last marked {int(time_diff_seconds)}s ago.")
                return  # Exit the function early

        # --- 2. If cooldown is over (or it's the first entry), insert new record ---
        c.execute(
            "INSERT INTO attendance (student_id, name, timestamp) VALUES (?, ?, ?)",
            (student_id, name, current_timestamp_str),
        )
        conn.commit()
        print(
            f"*** ATTENDANCE MARKED for {name} (ID: {student_id}) at {current_timestamp_str} ***"
        )

    except sqlite3.Error as e:
        print(f"Database error while marking attendance: {e}")

    finally:
        if conn:
            conn.close()


# Example of how to test this file directly (optional)
if __name__ == "__main__":
    print("Testing attendance module...")
    # Make sure you have a student with ID 'S101' in your 'students' table
    # You can add one using 'cli.py capture'
    mark_attendance("S101", "Test Student")
    print("First entry marked. Waiting 5 seconds and trying again...")
    import time

    time.sleep(5)
    mark_attendance("S101", "Test Student")
    print(
        "Test complete. Cooldown should have prevented the second entry (if cooldown > 5s)."
    )

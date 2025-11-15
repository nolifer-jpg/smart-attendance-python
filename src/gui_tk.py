# This script is for Coder 2.
# It creates a simple Tkinter GUI to run the main project commands.

import tkinter as tk
from tkinter import messagebox
import subprocess  # Used to run our other Python scripts
import threading  # To run scripts in a new thread so the GUI doesn't freeze
import sys
import csv
import sqlite3
from config.config import DB_PATH, ATTENDANCE_CSV_PATH, BASE_DIR

# --- Helper Function to run scripts ---


def run_script(command):
    """
    Runs a script (like 'capture' or 'encode') in a separate thread.
    This prevents the GUI from freezing while the script is running.

    We use 'subprocess.run' to execute the 'cli.py' script with arguments.
    """

    # We need to find the python executable
    python_exe = sys.executable  # Path to the current python interpreter

    # Path to the cli.py script
    cli_path = str(BASE_DIR / "src" / "cli.py")

    def target():
        try:
            print(f"Running command: {command}...")
            # This runs the command and waits for it to complete
            subprocess.run([python_exe, cli_path, command], check=True)
            print(f"Command '{command}' finished.")

            if command == "encode":
                messagebox.showinfo(
                    "Success", "Training complete! Encodings have been saved."
                )

        except subprocess.CalledProcessError as e:
            print(f"Error running command '{command}': {e}")
            messagebox.showerror("Error", f"Failed to run {command}.")
        except FileNotFoundError:
            print(
                "Error: 'python' command not found. Make sure Python is in your PATH."
            )
            messagebox.showerror("Error", "Python executable not found.")

    # Start the script in a new thread
    thread = threading.Thread(target=target)
    thread.start()


# --- GUI Command Functions ---


def gui_run_capture():
    messagebox.showinfo(
        "Capture", "Starting camera. Go to the console to enter student ID and name."
    )
    run_script("capture")


def gui_run_encode():
    messagebox.showinfo(
        "Encode",
        "Starting encoding... This may take a moment. See console for progress.",
    )
    run_script("encode")


def gui_run_recognizer():
    messagebox.showinfo(
        "Run", "Starting attendance system... Press 'q' in the OpenCV window to stop."
    )
    run_script("run")


def gui_export_csv():
    """Exports the 'attendance' table from the database to a CSV file."""
    print("Exporting attendance to CSV...")
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        c.execute("SELECT * FROM attendance")
        rows = c.fetchall()

        if not rows:
            messagebox.showinfo("Export", "No attendance records found to export.")
            return

        # Get header names from the cursor description
        headers = [description[0] for description in c.description]

        with open(ATTENDANCE_CSV_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)  # Write the header row
            writer.writerows(rows)  # Write all data rows

        messagebox.showinfo(
            "Export Complete", f"Attendance data saved to {ATTENDANCE_CSV_PATH}"
        )
        print(f"Export complete. Data saved to {ATTENDANCE_CSV_PATH}")

    except sqlite3.Error as e:
        print(f"Database error during export: {e}")
        messagebox.showerror("Error", f"Database error: {e}")
    except IOError as e:
        print(f"File error during export: {e}")
        messagebox.showerror("Error", f"File error: {e}")
    finally:
        if "conn" in locals() and conn:
            conn.close()


# --- Create the Main Window ---


def main_gui():
    root = tk.Tk()
    root.title("Smart Attendance System")
    root.geometry("400x350")

    # Set padding for the main frame
    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True, fill=tk.BOTH)

    # Title Label
    title_label = tk.Label(
        main_frame, text="Smart Attendance System", font=("Helvetica", 16, "bold")
    )
    title_label.pack(pady=(0, 20))

    # --- Create Buttons ---

    # Common button styling
    btn_font = ("Helvetica", 12)
    btn_width = 20
    btn_pady = 10

    # 1. Add New Student
    btn_capture = tk.Button(
        main_frame,
        text="1. Add New Student",
        command=gui_run_capture,
        font=btn_font,
        width=btn_width,
    )
    btn_capture.pack(pady=btn_pady)

    # 2. Train System
    btn_encode = tk.Button(
        main_frame,
        text="2. Train System",
        command=gui_run_encode,
        font=btn_font,
        width=btn_width,
    )
    btn_encode.pack(pady=btn_pady)

    # 3. Start Attendance
    btn_run = tk.Button(
        main_frame,
        text="3. Start Attendance",
        command=gui_run_recognizer,
        font=btn_font,
        width=btn_width,
        bg="#4CAF50",
        fg="white",
    )
    btn_run.pack(pady=btn_pady)

    # 4. Export CSV
    btn_export = tk.Button(
        main_frame,
        text="Export to CSV",
        command=gui_export_csv,
        font=btn_font,
        width=btn_width,
    )
    btn_export.pack(pady=(20, 0))  # Extra padding on top

    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main_gui()

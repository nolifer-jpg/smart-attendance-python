# This script is for Coder 2.
# It captures images from the webcam to add a new student to the system.

import cv2
import os
import sqlite3
from config.config import KNOWN_FACES_DIR, DB_PATH


def run_capture():
    """
    Captures and saves 10 face snapshots for a new student.
    Also adds the student's ID and name to the 'students' table in the database.
    """

    # 1. Get student info from the user
    student_id = input("Enter Student ID: ")
    name = input("Enter Student Name: ")

    if not student_id or not name:
        print("Student ID and Name cannot be empty. Exiting.")
        return

    # --- 2. Add student to the database ---
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        # 'INSERT OR IGNORE' prevents errors if the student_id already exists.
        # This is useful if you're just adding more photos for an existing student.
        c.execute(
            "INSERT OR IGNORE INTO students (student_id, name) VALUES (?, ?)",
            (student_id, name),
        )

        conn.commit()
        print(f"Student {name} (ID: {student_id}) added to database.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return
    finally:
        if conn:
            conn.close()

    # --- 3. Create a directory for the student's photos ---
    student_dir = KNOWN_FACES_DIR / student_id
    os.makedirs(
        student_dir, exist_ok=True
    )  # 'exist_ok=True' prevents error if folder already exists
    print(f"Directory created at {student_dir}")

    # --- 4. Initialize webcam ---
    cap = cv2.VideoCapture(0)  # 0 is the default webcam
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("\nStarting webcam. Look at the camera.")
    print("Press 's' to save a photo (10 required). Press 'q' to quit early.")

    count = 0
    while count < 10:
        # Read a frame from the webcam
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame. Exiting...")
            break

        # Display instructions on the video feed
        cv2.putText(
            frame,
            f"Press 's' to save ({count}/10)",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            frame,
            "Press 'q' to quit",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )

        # Show the video feed
        cv2.imshow("Capture Photos", frame)

        # Wait for a key press
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("Quitting capture...")
            break

        elif key == ord("s"):
            # Save the current frame as an image file
            img_name = f"{count + 1}.jpg"
            img_path = str(student_dir / img_name)

            cv2.imwrite(img_path, frame)
            print(f"Saved {img_path}")
            count += 1

    # --- 5. Clean up ---
    cap.release()
    cv2.destroyAllWindows()
    print(f"Captured {count} photos for {name}.")
    if count == 10:
        print("You can now run the 'encode' command to train the system.")


if __name__ == "__main__":
    run_capture()

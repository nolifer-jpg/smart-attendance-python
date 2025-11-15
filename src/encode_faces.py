# This is your task, Coder 1.
# This script reads all student images from 'data/known_faces/'
# and creates facial encodings, saving them to 'data/encodings.pkl'.

import face_recognition
import pickle
import os
import sqlite3
from config.config import KNOWN_FACES_DIR, ENCODINGS_PATH, DB_PATH


def run_encode():
    """
    Loops through all student images, generates facial encodings for each,
    and saves the encodings along with their corresponding names and IDs
    to a 'pickle' file.

    This 'pickle' file is a binary file that stores your Python object
    (in this case, a dictionary) so you can load it quickly later.
    """

    print("Starting face encoding...")

    # These lists will store all the encodings and their matching names/IDs
    known_face_encodings = []
    known_student_ids = []
    known_names = []

    # --- 1. Get student data from the database ---
    # This is better than just using folder names, as it's the "single source of truth".
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute("SELECT student_id, name FROM students")
        students = c.fetchall()  # Gets all (student_id, name) pairs
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return
    finally:
        if conn:
            conn.close()

    if not students:
        print("No students found in the database. Please run 'capture' first.")
        return

    # --- 2. Loop through each student and encode their images ---
    for student_id, name in students:
        print(f"Processing images for {name} (ID: {student_id})...")
        student_dir = KNOWN_FACES_DIR / student_id

        if not student_dir.exists():
            print(f"  WARNING: No image folder found for {name}. Skipping.")
            continue

        # Loop through each image file in the student's folder
        for img_path in student_dir.glob("*.jpg"):  # Find all .jpg files
            # Load the image file
            image = face_recognition.load_image_file(str(img_path))

            # Find face encodings.
            # This returns a list of encodings for all faces found in the image.
            # We assume there is only ONE face per image (the student's).
            encodings = face_recognition.face_encodings(image)

            if encodings:
                # Get the first (and hopefully only) encoding
                encoding = encodings[0]

                # Add the encoding and the student's info to our lists
                known_face_encodings.append(encoding)
                known_student_ids.append(student_id)
                known_names.append(name)
            else:
                print(f"  WARNING: No face found in {img_path}. Skipping.")

    print(f"\nTotal encodings generated: {len(known_face_encodings)}")

    # --- 3. Save the lists to a pickle file ---

    # We store all three lists in a dictionary for easy loading
    data = {
        "encodings": known_face_encodings,
        "ids": known_student_ids,
        "names": known_names,
    }

    # 'wb' means 'write binary' mode, which pickle requires
    with open(ENCODINGS_PATH, "wb") as f:
        pickle.dump(data, f)

    print(f"Encodings saved successfully to {ENCODINGS_PATH}")
    print("You can now run the 'run' command.")


if __name__ == "__main__":
    run_encode()

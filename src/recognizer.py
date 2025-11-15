# This is your task, Coder 1. This is the Core Engine.
# This script loads the encodings, opens the webcam,
# and performs real-time face recognition.

import cv2
import face_recognition
import pickle
import numpy as np  # NumPy is used for numerical operations
from config.config import ENCODINGS_PATH
from src.attendance import mark_attendance  # Import our attendance function


def run_recognizer():
    """
    This is the main function for the face recognition engine.
    It loads known faces and compares them to faces found in the webcam feed.
    """

    # --- 1. Load Known Faces and Encodings ---
    print("Loading known face encodings...")
    try:
        with open(ENCODINGS_PATH, "rb") as f:
            data = pickle.load(f)

        known_face_encodings = data["encodings"]
        known_student_ids = data["ids"]
        known_names = data["names"]
        print("Encodings loaded successfully.")
    except FileNotFoundError:
        print(f"Error: Encodings file not found at {ENCODINGS_PATH}.")
        print("Please run 'python src/cli.py encode' first.")
        return
    except Exception as e:
        print(f"Error loading encodings file: {e}")
        return

    # --- 2. Initialize Webcam ---
    video_capture = cv2.VideoCapture(0)  # 0 is the default webcam
    if not video_capture.isOpened():
        print("Error: Could not open webcam.")
        return
    print("Starting webcam... Press 'q' to quit.")

    # --- 3. Initialize variables for processing ---
    # These will hold the locations and encodings of faces found in the *current* frame
    face_locations = []
    face_encodings = []

    # This optimization processes only every other frame to save resources
    process_this_frame = True

    # --- 4. Start the Main Loop (runs for every frame) ---
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # --- Optimization ---
        # Only process every other frame to speed things up
        if process_this_frame:
            # Resize frame to 1/4 size for faster processing
            # (face_recognition works fine on smaller images)
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR (which OpenCV uses) to RGB (which face_recognition uses)
            # We use slicing [:, :, ::-1] which is a fast way to reverse the channels (B,G,R) -> (R,G,B)
            # Or you can use: rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            rgb_small_frame = small_frame[:, :, ::-1]

            # --- Find all faces and their encodings in the current frame ---
            # 'face_locations' finds the (top, right, bottom, left) coordinates of faces
            face_locations = face_recognition.face_locations(rgb_small_frame)

            # 'face_encodings' gets the 128-point encoding for each face found
            face_encodings = face_recognition.face_encodings(
                rgb_small_frame, face_locations
            )

            # Loop through each face found in this frame
            for face_encoding in face_encodings:
                # --- Compare the found face with all known faces ---

                # 'compare_faces' returns a list of True/False values
                # e.g., [True, False, False] if it matched the first known person
                matches = face_recognition.compare_faces(
                    known_face_encodings, face_encoding
                )

                name = "Unknown"
                student_id = None

                # 'face_distance' gives a "distance" score for each comparison.
                # A lower distance means a better match.
                face_distances = face_recognition.face_distance(
                    known_face_encodings, face_encoding
                )

                # 'np.argmin' finds the index (position) of the *lowest* distance
                best_match_index = np.argmin(face_distances)

                # If the best match's 'matches' value is True, we have a winner
                if matches[best_match_index]:
                    name = known_names[best_match_index]
                    student_id = known_student_ids[best_match_index]

                # --- Mark Attendance ---
                if student_id:
                    # Call our function from attendance.py
                    mark_attendance(student_id, name)

        # This toggles the flag so the *next* frame is skipped
        process_this_frame = not process_this_frame

        # --- 5. Display the Results (runs every frame) ---

        # We draw boxes *after* the processing block, so the video looks smooth
        # even on skipped frames (it just shows the boxes from the *last* processed frame)

        # Loop through each face location *and* its determined name
        # We zip `face_locations` (from processing) and the `name` (which we just found)
        # Note: This part needs to be adjusted. We need to store names from the loop.

        # Let's re-think: We should loop face_locations *and* encodings together.
        # The logic above is slightly wrong. Let's fix it.

        # (This is how the loop *should* be, inside 'if process_this_frame:')
        # face_names_and_ids = []
        # for face_encoding in face_encodings:
        #    ... (comparison logic) ...
        #    face_names_and_ids.append((name, student_id))

        # (The original code is simpler, let's stick to it, but we need to display)

        # --- 5. Display the Results (drawing boxes) ---
        # This loop draws boxes on the *original, full-sized frame*

        for (top, right, bottom, left), face_encoding in zip(
            face_locations, face_encodings
        ):
            # --- Re-run comparison logic to get the name for this box ---
            # (This is slightly inefficient, but easier to understand)
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding
            )
            name = "Unknown"

            face_distances = face_recognition.face_distance(
                known_face_encodings, face_encoding
            )
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = known_names[best_match_index]
                # We don't need to call mark_attendance here, we did it in the logic block

            # --- Draw the boxes ---

            # Scale the face locations back up (we multiplied by 0.25 earlier)
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a green box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Draw a filled green rectangle for the name label
            cv2.rectangle(
                frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED
            )
            font = cv2.FONT_HERSHEY_DUPLEX

            # Put the name text (in white) on the label
            cv2.putText(
                frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1
            )

        # Display the resulting image in a window
        cv2.imshow("Attendance System", frame)

        # --- 6. Check for 'q' key to quit ---
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("Quitting...")
            break

    # --- 7. Clean up ---
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_recognizer()

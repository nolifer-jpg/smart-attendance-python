# Smart Attendance System

This is a 1st-year university project that uses Python and face recognition to take attendance automatically.

## Features
* **Add Students**: Capture photos of new students from a webcam.
* **Train System**: Generate and save face encodings from the captured photos.
* **Mark Attendance**: Run the recognizer to identify students in real-time and mark their attendance in an SQLite database.
* **Database**: Uses a simple SQLite database to store student info and attendance logs.
* **GUI**: An optional Tkinter GUI to run the main commands.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone [your-repo-url]
    cd smart-attendance-system
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create your environment file:**
    * Copy `.env.example` to a new file named `.env`.
    * (Optional) Fill in your email details if you implement the alerts feature.

## Usage (Command Line)

You must run the commands in this order:

1.  **Initialize the Database:**
    * This creates the `students.db` file and the necessary tables.
    ```bash
    python src/cli.py init_db
    ```

2.  **Add Students (Capture):**
    * This will ask for a Student ID and Name, then open the webcam.
    * Press **'s'** to save a photo. It will save 10 photos and then quit.
    * Press **'q'** to quit early.
    ```bash
    python src/cli.py capture
    ```

3.  **Train the System (Encode):**
    * This reads all images in `data/known_faces/`, generates encodings, and saves them to `data/encodings.pkl`.
    * You **must** re-run this every time you add a new student.
    ```bash
    python src/cli.py encode
    ```

4.  **Run the Attendance System:**
    * This opens the webcam and starts recognizing students.
    * Attendance is logged in `students.db`.
    * Press **'q'** to stop the program.
    ```bash
    python src/cli.py run
    ```

## Usage (GUI)

You can also use the simple Graphical User Interface.

```bash
python src/gui_tk.py
```
* **"Add New Student"**: Runs the capture script.
* **"Train System"**: Runs the encoding script.
* **"Start Attendance"**: Runs the recognizer.
* **"Export CSV"**:Saves the attendance log to `data/attendance.csv`.

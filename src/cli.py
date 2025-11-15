# This is your task, Coder 1.
# This file is the main entry point for the command line.
# It uses 'argparse' to handle commands like 'run', 'capture', etc.

import argparse

# Import the main functions from our other modules
from src.db import create_database
from src.capture import run_capture
from src.encode_faces import run_encode
from src.recognizer import run_recognizer


def main():
    """
    Main function to parse command-line arguments and run the corresponding command.
    """

    # Create the main parser
    parser = argparse.ArgumentParser(
        description="Smart Attendance System CLI",
        formatter_class=argparse.RawTextHelpFormatter,  # Helps format the help text nicely
    )

    # Define the 'command' argument.
    # 'choices' limits the user to only the commands we've defined.
    parser.add_argument(
        "command",
        choices=["init_db", "capture", "encode", "run"],
        help="""The command to execute:
  init_db  - Initialize the database and create tables.
  capture  - Capture faces for a new student.
  encode   - Encode all known faces and save to .pkl file.
  run      - Start the real-time attendance recognizer.
""",
    )

    # Parse the arguments from the command line
    args = parser.parse_args()

    # --- Execute the chosen command ---

    if args.command == "init_db":
        print("Initializing database...")
        create_database()

    elif args.command == "capture":
        print("Running student capture...")
        run_capture()

    elif args.Scommand == "encode":
        print("Running face encoding...")
        run_encode()

    elif args.command == "run":
        print("Starting attendance system...")
        run_recognizer()


# This is the standard Python entry point.
# If this file is run directly (e.g., 'python src/cli.py run'),
# the main() function will be called.
if __name__ == "__main__":
    main()

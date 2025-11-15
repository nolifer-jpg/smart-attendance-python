# test_imports.py

# pytest will run any function that starts with 'test_'
def test_all_imports_are_installed():
    """
    This test just tries to import every library.
    If an ImportError occurs, pytest will mark this test as FAILED.
    """
    import cv2
    import face_recognition
    import numpy
    import PIL
    import dotenv
    import sqlite3
    import tkinter

    # If we get here without an error, the test passes
    assert True

# This script is for Coder 2.
# It provides a simple function for sending email alerts.
# For now, it just prints to the console.

import smtplib
from config.config import EMAIL_USER, EMAIL_PASSWORD


def send_alert_email(student_name, student_id):
    """
    Sends an alert email.
    Currently, this is a placeholder and just prints to the console.

    To implement this, you would need to:
    1. Fill in EMAIL_USER and EMAIL_PASSWORD in your .env file.
    2. Use a Google "App Password" if using Gmail (standard password won't work).
    3. Uncomment the 'smtplib' code below.
    """

    subject = "Attendance System Alert"
    body = f"Alert: An unrecognized person was detected, but they closely matched {student_name} (ID: {student_id}). Please review."
    message = f"Subject: {subject}\n\n{body}"

    print("--- ALERT ---")
    print(f"Email alert would be sent to admin about {student_name}.")
    print(f"Message: {body}")
    print("-------------")

    # --- Real Email Logic (Optional) ---
    # if not EMAIL_USER or not EMAIL_PASSWORD:
    #     print("Email credentials not set in .env file. Cannot send real email.")
    #     return
    #
    # try:
    #     # Connect to Gmail's SMTP server
    #     server = smtplib.SMTP('smtp.gmail.com', 587)
    #     server.starttls()  # Secure the connection
    #     server.login(EMAIL_USER, EMAIL_PASSWORD)
    #
    #     # Send the email
    #     # Note: You'd want to send TO an admin email, not just FROM the user email
    #     admin_email = "admin@example.com"
    #     server.sendmail(EMAIL_USER, admin_email, message)
    #
    #     print("Successfully sent email alert.")
    #
    # except Exception as e:
    #     print(f"Failed to send email: {e}")
    #
    # finally:
    #     if 'server' in locals():
    #         server.quit()


if __name__ == "__main__":
    # Test the function
    send_alert_email("Test Student", "S101")

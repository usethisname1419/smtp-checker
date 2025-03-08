import smtplib
import imaplib
import email
import time

def smtp_check(smtp_server, port, sender_email, password, recipient_email, use_tls=True):
    """Check if SMTP can send an email to the inbox."""
    try:
        server = smtplib.SMTP(smtp_server, port, timeout=10)
        if use_tls:
            server.starttls()
        
        server.login(sender_email, password)

        # Construct the email message
        msg = f"From: {sender_email}\r\nTo: {recipient_email}\r\nSubject: SMTP Test\r\n\r\nThis is a test email."
        
        server.sendmail(sender_email, recipient_email, msg)
        server.quit()

        print("[+] Email sent successfully!")
        return True
    except Exception as e:
        print(f"[-] SMTP Error: {e}")
        return False

def check_inbox(imap_server, email_user, email_pass, subject="SMTP Test", wait_time=10):
    """Check if the email was received in the inbox."""
    try:
        print("[*] Checking inbox for test email...")
        time.sleep(wait_time)  # Wait a few seconds for delivery

        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select("inbox")

        result, data = mail.search(None, 'ALL')
        email_ids = data[0].split()

        for email_id in reversed(email_ids):  # Check latest emails first
            result, msg_data = mail.fetch(email_id, '(RFC822)')
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            if subject in msg["Subject"]:
                print("[+] Email received in inbox!")
                return True

        print("[-] Email NOT found in inbox.")
        return False
    except Exception as e:
        print(f"[-] IMAP Error: {e}")
        return False

if __name__ == "__main__":
    smtp_server = input("SMTP Server: ")
    smtp_port = int(input("SMTP Port (usually 587 for TLS, 465 for SSL): "))
    sender_email = input("Sender Email: ")
    sender_password = input("Sender Password: ")
    recipient_email = input("Recipient Email: ")
    use_tls = input("Use TLS? (yes/no): ").strip().lower() == "yes"

    imap_server = input("IMAP Server (for inbox check, leave empty to skip): ")
    email_user = sender_email  # Usually the same as sender
    email_pass = sender_password  # Usually the same password

    if smtp_check(smtp_server, smtp_port, sender_email, sender_password, recipient_email, use_tls):
        if imap_server:
            check_inbox(imap_server, email_user, email_pass)

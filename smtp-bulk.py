import smtplib
import imaplib
import email
import time
import argparse

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

        print(f"[+] Email sent successfully from {sender_email}!")
        return True
    except Exception as e:
        print(f"[-] SMTP Error ({sender_email}): {e}")
        return False

def check_inbox(imap_server, email_user, email_pass, subject="SMTP Test", wait_time=10):
    """Check if the email was received in the inbox."""
    try:
        print(f"[*] Checking inbox for {email_user}...")
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
                print(f"[+] Email received in inbox for {email_user}!")
                return True

        print(f"[-] Email NOT found in inbox for {email_user}.")
        return False
    except Exception as e:
        print(f"[-] IMAP Error ({email_user}): {e}")
        return False

def process_bulk(file_path, recipient_email, use_tls=True):
    """Process bulk credentials from a file and check SMTP/IMAP."""
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    for line in lines:
        try:
            smtp_server, port, sender_email, sender_password = line.strip().split(":")
            port = int(port)
            imap_server = smtp_server.replace("smtp", "imap")
            
            if smtp_check(smtp_server, port, sender_email, sender_password, recipient_email, use_tls):
                check_inbox(imap_server, sender_email, sender_password)
        except ValueError:
            print(f"[-] Invalid format: {line.strip()}")
        except Exception as e:
            print(f"[-] Unexpected error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SMTP and IMAP Email Checker")
    parser.add_argument("--smtp_server", help="SMTP Server")
    parser.add_argument("--smtp_port", type=int, help="SMTP Port (587 for TLS, 465 for SSL)")
    parser.add_argument("--sender_email", help="Sender Email")
    parser.add_argument("--sender_password", help="Sender Password")
    parser.add_argument("--recipient_email", help="Recipient Email")
    parser.add_argument("--use_tls", choices=["yes", "no"], default="yes", help="Use TLS (yes/no)")
    parser.add_argument("--imap_server", help="IMAP Server (for inbox check, leave empty to skip)")
    parser.add_argument("--bulk", help="Path to bulk credentials file", default=None)
    
    args = parser.parse_args()
    use_tls = args.use_tls.lower() == "yes"
    
    if args.bulk:
        process_bulk(args.bulk, args.recipient_email, use_tls)
    else:
        if smtp_check(args.smtp_server, args.smtp_port, args.sender_email, args.sender_password, args.recipient_email, use_tls):
            if args.imap_server:
                check_inbox(args.imap_server, args.sender_email, args.sender_password)

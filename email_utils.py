import smtplib
import imaplib
import email
import email.mime.multipart as mp
import email.mime.text as mt
import socket
import ssl

class EmailError(Exception):
    """
    Custom exception for email-related errors
    """
    pass
def send_email(sender_email, sender_password, receiver_email, subject, body):
    """
    Sends email using Gmail SMTP server

    Parameters:

    sender_email (str): Sender's email address
    sender_password (str): Sender's email password
    receiver_email (str): Receiver's email address
    subject (str): Email subject
    body (str): Email body

    Returns:
    None
    """
    try:
        # SMTP server settings
        smtp_server = "smtp.gmail.com"
        smtp_port = 465
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)

        # Login to the email server
        server.login(sender_email, sender_password)

        # Create the email message
        message = mp.MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(mt.MIMEText(body, "plain"))

        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())

        server.quit()


        print("Email sent successfully")
    # Handles common exceptions
    except smtplib.SMTPAuthenticationError as e:
        raise EmailError("Authentication failed. Please check your email and password." + str(e))
    except smtplib.SMTPConnectError as e:
        raise EmailError("Could not connect to the SMTP server. Please check your internet connection." + str(e))
    except smtplib.SMTPDataError as e:
        raise EmailError("Mail was rejected by the server." + str(e))
    except smtplib.SMTPHeloError as e:
        raise EmailError("The server didn’t reply properly to the HELO greeting." + str(e))
    except smtplib.SMTPRecipientsRefused as e:
        raise EmailError("All recipients were refused. Nobody got the mail." + str(e))
    except smtplib.SMTPServerDisconnected as e:
        raise EmailError("The server unexpectedly disconnected." + str(e))
    except socket.gaierror as e:
        raise EmailError("The address couldn’t be resolved." + str(e))
    except ssl.SSLError as e:
        raise EmailError("The SSL handshake failed." + str(e))
    except smtplib.SMTPException as e:
        raise EmailError("An SMTP error occurred." + str(e))
    except Exception as e:
        raise EmailError("An error occurred." + str(e))


def fetch_latest_email(email_address, password):
    """
    Fetches the latest email from the user's inbox
    :param email_address: Email address
    :param password: Email password
    :return:
    """
    try:
        # IMAP server settings
        imap_server = "imap.gmail.com"
        imap_port = 993


        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, password)
        mail.select("Inbox")

        # Fetch the latest email
        result, data = mail.search(None, "ALL")

        # Check if the search was successful
        if result != "OK":
            print("Error fetching emails")
            return

        # Get the email IDs
        email_ids = data[0].split()
        if not email_ids:
            print("No emails found")
            return

        latest_email = email_ids[-1]
        result, data = mail.fetch(latest_email, "(RFC822)")

        if result != "OK":
            print("Error fetching email")
            return

        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = msg["Subject"]
        sender = msg["From"]
        text_body = ""  # For plain text emails
        html_body = ""  # For HTML emails
        attachments = []  # List to store attachment details

        # **Extract email content**
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # **Extract plain text body**
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    text_body += part.get_payload(decode=True).decode(errors="ignore") + "\n"

                # **Extract HTML body**
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    html_body += part.get_payload(decode=True).decode(errors="ignore") + "\n"

                # **Handle attachments**
                elif "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            "filename": filename,
                            "data": part.get_payload(decode=True)  # Binary data of the file
                        })

        else:
            # Non-multipart email (single-part message)
            text_body = msg.get_payload(decode=True).decode(errors="ignore")
        mail.logout()

        # Return extracted content**
        return {
            "subject": subject,
            "sender": sender,
            "text_body": text_body.strip(),
            "html_body": html_body.strip(),
            "attachments": attachments
        }

    # Handles common exceptions
    except imaplib.IMAP4.error:
        raise EmailError("IMAP login failed. Check your email and password.")
    except socket.gaierror:
        raise EmailError("Network error. Could not resolve server address.")
    except ssl.SSLError:
        raise EmailError("SSL connection failed.")
    except Exception as e:
        raise EmailError(f"An unexpected error occurred: {str(e)}")

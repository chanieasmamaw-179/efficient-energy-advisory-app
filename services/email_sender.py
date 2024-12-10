"""
This module handles the import of necessary libraries and configurations for sending emails
using MailerSend and loading environment variables from a .env file.
"""
# Standard library imports
import os
import logging

# Third-party imports
from dotenv import load_dotenv
from mailersend import emails

# Load environment variables
load_dotenv()

MAILERSEND_API_KEY = os.getenv("MAILERSEND_API_KEY")

if not MAILERSEND_API_KEY:
    raise ValueError("MailerSend API key is not set.")

# Set up logger
logger = logging.getLogger("main")
logging.basicConfig(level=logging.INFO)


def send_email_dynamic(
        sender: dict,
        recipient: dict,
        subject: str,
        html_content: str,
        text_content: str,
        reply_to: dict = None,
):
    """
    Send email using MailerSend with proper newline formatting.

    Args:
        sender (dict): Sender's name and email.
        recipient (dict): Recipient's name and email.
        subject (str): Email subject.
        html_content (str): HTML email content.
        text_content (str): Plain text email content.
        reply_to (dict): Reply-to address (optional).
    """
    # Convert newlines (\n) to HTML <br> tags for HTML content
    formatted_html_content = html_content.replace("\n", "<br>")

    try:
        # Initialize MailerSend email client
        mailer = emails.NewEmail(MAILERSEND_API_KEY)

        # Build the email body
        mail_body = {}
        mailer.set_mail_from(sender, mail_body)
        mailer.set_mail_to([recipient], mail_body)
        mailer.set_subject(subject, mail_body)

        # Assign content with properly formatted newlines
        mailer.set_html_content(formatted_html_content, mail_body)
        mailer.set_plaintext_content(text_content, mail_body)

        if reply_to:
            mailer.set_reply_to(reply_to, mail_body)

        # Send the email
        logger.info("Sending email to %s with subject '%s'", recipient['email'], subject)
        response = mailer.send(mail_body)
        logger.info("MailerSend response %s:", {response})
        return response

    except Exception as e:
        logger.error("Failed to send email to %s: %s", recipient['email'], str(e))
        raise RuntimeError(f"Failed to send email: {e}") from e

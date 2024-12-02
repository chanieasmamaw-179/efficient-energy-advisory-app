import pytest
from unittest.mock import MagicMock, patch
from services.email_sender import send_email_dynamic

# Test data
SENDER = {"name": "Test Sender", "email": "sender@example.com"}
RECIPIENT = {"name": "Test Recipient", "email": "recipient@example.com"}
SUBJECT = "Test Subject"
HTML_CONTENT = "This is a test email.\nNew line."
TEXT_CONTENT = "This is a test email.\nNew line."
REPLY_TO = {"name": "Reply To", "email": "replyto@example.com"}

@patch("email_sender.emails.NewEmail")
def test_send_email_success(mock_new_email):
    """
    Test successful email sending with MailerSend.
    """
    # Mock the MailerSend API client
    mock_mailer_instance = MagicMock()
    mock_new_email.return_value = mock_mailer_instance
    mock_mailer_instance.send.return_value = {"status": "success"}

    response = send_email_dynamic(
        sender=SENDER,
        recipient=RECIPIENT,
        subject=SUBJECT,
        html_content=HTML_CONTENT,
        text_content=TEXT_CONTENT,
        reply_to=REPLY_TO,
    )

    # Assertions
    mock_new_email.assert_called_once_with("MAILERSEND_API_KEY")
    mock_mailer_instance.set_mail_from.assert_called_once_with(SENDER, {})
    mock_mailer_instance.set_mail_to.assert_called_once_with([RECIPIENT], {})
    mock_mailer_instance.set_subject.assert_called_once_with(SUBJECT, {})
    mock_mailer_instance.set_html_content.assert_called_once_with(
        HTML_CONTENT.replace("\n", "<br>"), {}
    )
    mock_mailer_instance.set_plaintext_content.assert_called_once_with(TEXT_CONTENT, {})
    mock_mailer_instance.set_reply_to.assert_called_once_with(REPLY_TO, {})
    mock_mailer_instance.send.assert_called_once()
    assert response == {"status": "success"}

@patch("email_sender.emails.NewEmail")
def test_send_email_failure(mock_new_email):
    """
    Test email sending failure due to an exception.
    """
    # Mock the MailerSend API client to raise an exception
    mock_mailer_instance = MagicMock()
    mock_new_email.return_value = mock_mailer_instance
    mock_mailer_instance.send.side_effect = Exception("Mock API error")

    with pytest.raises(RuntimeError) as exc_info:
        send_email_dynamic(
            sender=SENDER,
            recipient=RECIPIENT,
            subject=SUBJECT,
            html_content=HTML_CONTENT,
            text_content=TEXT_CONTENT,
            reply_to=REPLY_TO,
        )

    # Assertions
    mock_new_email.assert_called_once_with("MAILERSEND_API_KEY")
    mock_mailer_instance.send.assert_called_once()
    assert "Failed to send email" in str(exc_info.value)
    assert "Mock API error" in str(exc_info.value)

@patch("email_sender.os.getenv")
def test_missing_mailersend_api_key(mock_getenv):
    """
    Test handling of missing MailerSend API key.
    """
    mock_getenv.return_value = None  # Simulate missing API key

    with pytest.raises(ValueError) as exc_info:
        send_email_dynamic(
            sender=SENDER,
            recipient=RECIPIENT,
            subject=SUBJECT,
            html_content=HTML_CONTENT,
            text_content=TEXT_CONTENT,
        )

    # Assertions
    assert "MailerSend API key is not set." in str(exc_info.value)

@patch("email_sender.emails.NewEmail")
def test_email_dynamic_html_formatting(mock_new_email):
    """
    Test that newlines in HTML content are properly converted to <br> tags.
    """
    # Mock the MailerSend API client
    mock_mailer_instance = MagicMock()
    mock_new_email.return_value = mock_mailer_instance
    mock_mailer_instance.send.return_value = {"status": "success"}

    send_email_dynamic(
        sender=SENDER,
        recipient=RECIPIENT,
        subject=SUBJECT,
        html_content=HTML_CONTENT,
        text_content=TEXT_CONTENT,
    )

    # Assert that HTML content was formatted correctly
    expected_html = HTML_CONTENT.replace("\n", "<br>")
    mock_mailer_instance.set_html_content.assert_called_once_with(expected_html, {})


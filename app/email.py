# from flask_mailman import EmailMessage, EmailMultiAlternatives
import base64
import os
from flask import render_template, current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

def send_email(subject, from_email, to, body, html_content, attachments=None):
    message = Mail(
        from_email=from_email,
        to_emails=to,
        subject=subject,
        html_content=html_content,
        plain_text_content=body
    )
    if attachments:
        for attachment in attachments:
            with open(attachment[0], 'rb') as f:
                file_data = f.read()
            encoded_file = FileContent(str(base64.b64encode(file_data), 'utf-8'))
            attachment = Attachment(
                FileContent(encoded_file),
                FileName(attachment[1]),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            message.attachment = attachment

    try:
        sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        return response
    except Exception as e:
        print(str(e))
        return None



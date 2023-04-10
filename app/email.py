import base64
from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition


def send_email(subject, from_email, to, html_content, attachments=None):
    """Uses sendgrid to send email"""
    message = Mail(
        from_email=from_email,
        to_emails=to,
        subject=subject,
        html_content=html_content,
    )
    print(from_email)
    if attachments:
        for attachment in attachments:
            file_name, file_content, file_type = attachment
            encoded_content = base64.b64encode(file_content.encode()).decode()
            attachment = Attachment()
            attachment.file_content = FileContent(encoded_content)
            attachment.file_name = FileName(file_name)
            attachment.file_type = FileType(file_type)
            attachment.disposition = Disposition('attachment')

            message.add_attachment(attachment)

    try:
        print(0)
        sg = SendGridAPIClient(current_app.config['SENDGRID_API_KEY'])
        response = sg.send(message)
        print(1)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))
        return None

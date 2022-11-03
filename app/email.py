from flask_mailman import EmailMessage, EmailMultiAlternatives
from app import mail
from flask import render_template, current_app


def send_email(subject, from_email, to, body, html_content):
    text_content = body
    html_content = html_content
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()



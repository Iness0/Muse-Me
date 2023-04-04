from flask import render_template, current_app
from app.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Muse Me] Password Reset', from_email=current_app.config['SENDGRID_EMAIL'], to=user.email,
               html_content=render_template('email/reset_password.html', user=user, token=token))

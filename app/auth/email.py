from flask import render_template, current_app
from app.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Microblog] Password Reset', from_email=app.config['ADMINS'][0],
               to=user.email, body=render_template('email/reset_password.txt', user=user, token=token),
               html_content=render_template('email/reset_password.html', user=user, token=token))

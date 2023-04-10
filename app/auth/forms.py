from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _1
from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_('Username'), validators=[DataRequired()])
    password = PasswordField(_('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_('Remember Me'))
    submit = SubmitField(_('Sign In'))


class RegisterForm(FlaskForm):
    username = StringField(_('Username'), validators=[DataRequired()])
    email = EmailField(_('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_('Password'), validators=[DataRequired()])
    password_repeat = PasswordField(_('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('This username already exists'))

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError(_('This email already registered, please Log In'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_('Password'), validators=[DataRequired()])
    password2 = PasswordField(_('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_('Request Password Reset'))


class ResetPasswordFormAuthorized(FlaskForm):
    current_password = PasswordField(_('Current Password'), validators=[DataRequired()])
    password = PasswordField(_('Password'), validators=[DataRequired()])
    password2 = PasswordField(_('Confirm Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_('Update Password'))

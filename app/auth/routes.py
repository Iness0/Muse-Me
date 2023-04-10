from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, g
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _, get_locale
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordRequestForm, ResetPasswordForm, \
    ResetPasswordFormAuthorized
from app.main.forms import SearchForm
from app.models import User
from app.auth.email import send_password_reset_email


@bp.before_request
def before_request():
    """Executed before each request. Sets up search form and locale."""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Logs in the user."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        else:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registers a new user."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'), form=form)


@bp.route('/logout')
def logout():
    """Logs out the user."""
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Sends an email to the user to reset their password."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for further instructions'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Allows a user to reset their password.

    :param token: A token to verify the user.
    :type token: str
    :return: If the user is authenticated, redirects to main index. If the user is not found, redirects to main index.
             Otherwise, renders the reset password page and resets the user's password if the form is valid.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/reset_password', methods=['POST'])
def password_reset():
    """
    Allows a user to change their password.
    """
    form = ResetPasswordFormAuthorized()
    if form.validate_on_submit():
        if current_user.check_password(form.password.data):
            flash(_('You cant change password to the same password'))
            return redirect(url_for('main.edit_profile'))
        elif current_user.check_password(form.current_password.data):
            current_user.set_password(form.password.data)
            db.session.commit()
            flash(_('Your password has been changed successfully'))
            return redirect(url_for('main.edit_profile'))
        else:
            flash(_('Your current password is incorrect'))
            return redirect(url_for('main.edit_profile'))
    flash(_('there has been an error with your password'))
    return redirect(url_for('main.edit_profile'))


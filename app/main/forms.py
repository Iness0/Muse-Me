from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import TextAreaField, StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import Length, DataRequired, Email, EqualTo, ValidationError
from app.models import User
from flask_babel import lazy_gettext as _1, _
from flask import request


class EditProfileForm(FlaskForm):
    username = StringField(_1('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_1('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_1('Submit'))

    def __init__(self, original_name, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_username(self, username):
        if username.data != self.original_name:
            user = User.query.filter_by(username=self.username).first()
            if user is not None:
                raise  ValidationError(_('Please use different name'))


class EmptyForm(FlaskForm):
    submit = SubmitField(_1('Submit'))


class PostForm(FlaskForm):
    post = TextAreaField(_1('Say something'), validators=[
        DataRequired(), Length(min=1, max=140)])
    image = FileField('Image', validators=[
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])
    submit = SubmitField(_1('Submit'))


class SearchForm(FlaskForm):
    q = StringField(_1('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)


class MessageForm(FlaskForm):
    message = TextAreaField(_1('Message'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_1('Submit'))

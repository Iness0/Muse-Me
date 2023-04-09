import os

from flask import flash, redirect, url_for, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename

from app import db
from app.main.forms import EmptyForm
from app.models import Post, User, Image


def main_variables(_user=None):
    popular_people = current_user.get_popular()
    hashtag_counts = Post.get_all_tags()
    form = EmptyForm()
    if _user is not None:
        images = _user.images.limit(4).all()
        return popular_people, hashtag_counts, images, form
    return popular_people, hashtag_counts, form


def get_user_from_username(username):
    user = User.query.filter(User.username == username).first()
    if user is None:
        flash('User not found.')
        return redirect(url_for('main.index'))
    return user


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_FILES']


def save_image(image):
    if not allowed_file(image.filename):
        flash(_('Image extension not allowed'))
        return 1
    filename = secure_filename(image.filename)
    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    image = Image(filename=filename, user_id=current_user.id)
    db.session.add(image)
    return image

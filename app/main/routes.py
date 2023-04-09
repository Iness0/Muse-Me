import os
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, abort
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from langdetect import detect, LangDetectException
from sqlalchemy.orm import subqueryload
from werkzeug.utils import secure_filename
from app import db
from app.auth.forms import ResetPasswordFormAuthorized
from app.main.forms import MessageForm, EditProfileForm, EmptyForm, PostForm, SearchForm, CommentForm
from app.main.helpers import get_user_from_username, main_variables, allowed_file, save_image
from app.models import User, Post, Message, Notification, Reaction, Comment, followers, Image
from app.main import bp


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['POST', 'GET'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if request.method == 'POST':
        text = request.form.get('post')
        try:
            language = detect(text)
        except LangDetectException:
            language = ''
        image_file = request.files.getlist('images[]')
        if image_file and any(image for image in image_file):
            post = Post(body=text, author=current_user, language=language)
            for image in image_file:
                new_image = save_image(image)
                new_image.post = post
        else:
            post = Post(body=text, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().options(subqueryload('images')).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    popular_people, hashtag_counts = main_variables()[:2]
    comment_form = CommentForm()

    for post in posts.items:
        amount = post.comments.count()
        post.show_more_comments = amount > 3

    return render_template('index.html', form=form, title=(_('Home')), posts=posts.items,
                           next_url=next_url, prev_url=prev_url, hashtag_counts=hashtag_counts,
                           popular_people=popular_people, comment_form=comment_form)


@bp.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    post_id = request.args.get('post_id')
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, user_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        flash(_('Your comment has been added.'))
        return redirect(request.referrer)
    return redirect(request.referrer)


def create_or_update_reaction(user_id, target_id, emoji, target_type):
    if target_type == 'post':
        target_column = Reaction.post_id
    elif target_type == 'comment':
        target_column = Reaction.comment_id
    else:
        target_column = Reaction.image_id
    reaction = Reaction.query.filter_by(user_id=user_id, **{target_column.name: target_id}).first()

    if reaction is None:
        reaction = Reaction(user_id=user_id, **{target_column.name: target_id}, emoji=emoji)
        db.session.add(reaction)
    elif emoji is None or emoji == reaction.emoji:
        db.session.delete(reaction)
        db.session.commit()
        return None
    else:
        reaction.emoji = emoji
    db.session.commit()
    return reaction


@bp.route('/user/<username>')
@login_required
def user(username):
    user = get_user_from_username(username)
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = PostForm()
    for post in posts.items:
        amount = post.comments.count()
        post.show_more_comments = amount > 3
    comment_form = CommentForm()
    popular_people, hashtag_counts, images = main_variables(user)[:3]
    return render_template('user.html', title=username, user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form, comment_form=comment_form,
                           images=images, hashtag_counts=hashtag_counts, popular_people=popular_people)


@bp.route('/user/<username>/<string:relation>')
@login_required
def followers(username, relation):
    user = get_user_from_username(username)
    if relation == 'following':
        users = user.followed.all()
    elif relation == 'followers':
        users = user.followers.all()
    else:
        abort(404)
    popular_people, hashtag_counts, images, form = main_variables(user)
    return render_template('followers.html', title=username, user=user, users=users,
                           form=form, images=images, hashtag_counts=hashtag_counts, popular_people=popular_people)


@bp.route('/edit_profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    password_form = ResetPasswordFormAuthorized()
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        # avatar
        if form.avatar.data:
            current_user.avatar = save_image(form.avatar.data).filename
            # Save background image
        if form.background_image.data:
            current_user.background_image = save_image(form.background_image.data).filename
        db.session.commit()
        print(current_user.avatar)
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.firstname = current_user.first_name
        form.lastname = current_user.last_name
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form, password_form=password_form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = get_user_from_username(username)
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are now following {username}!')
        return redirect(request.referrer or url_for('main.user', username=username))
    else:
        return redirect(request.referrer or url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = get_user_from_username(username)
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_(f'You are no longer following {username}!'))
        return redirect(request.referrer or url_for('main.user', username=username))
    else:
        return redirect(request.referrer or url_for('main.index'))


@bp.route('/explore')
@login_required
def explore():
    comment_form = CommentForm()
    page = request.args.get('page', 1, type=int)
    subquery = db.session.query(db.metadata.tables['followers'].c.followed_id).filter_by(
        follower_id=current_user.id).subquery()
    posts = Post.query.filter(db.and_(Post.user_id != current_user.id, ~Post.user_id.in_(subquery))).order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    popular_people, hashtag_counts, form = main_variables()
    for post in posts.items:
        amount = post.comments.count()
        post.show_more_comments = amount > 3
    return render_template('index.html', title=_('Explore'), posts=posts.items,
                           next_url=next_url, prev_url=prev_url, hashtag_counts=hashtag_counts,
                           popular_people=popular_people, form=form, comment_form=comment_form, post_exclude=True)


@bp.route('/search')
@login_required
def search():
    comment_form = CommentForm()
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url, comment_form=comment_form)


@bp.route('/messages', methods=['POST', 'GET'])
@login_required
def messages():
    page = request.args.get('page', 1, type=int)
    id = request.args.get('user')
    user = User.query.get(id)
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(
            author=current_user,
            recipient=user,
            body=form.message.data
        )
        user.add_notification('unread_message_count', user.new_messages())
        db.session.add(msg)
        db.session.commit()
        flash(_('Your message has been sent.'))
        return redirect(url_for('main.messages', user=id))
    if id:
        return handle_personal_messages(page, id, user)
    else:
        return handle_conversations(page)


def handle_personal_messages(page, user_id, user):
    form = MessageForm()
    last_messages = Message.query.filter(
        db.or_(
            db.and_(Message.sender_id == current_user.id, Message.recipient_id == user_id),
            db.and_(Message.sender_id == user_id, Message.recipient_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).all()
    return render_template('personal_messages.html', form=form, messages=last_messages, user=user)


def handle_conversations(page):
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()

    subquery = db.session.query(
        db.func.max(Message.timestamp).label('max_timestamp'),
        db.case([(Message.sender_id == current_user.id, Message.recipient_id),
                 (Message.recipient_id == current_user.id, Message.sender_id)]).label('conversation')
    ).filter(db.or_(Message.sender_id == current_user.id, Message.recipient_id == current_user.id)
             ).group_by('conversation').subquery()

    last_messages = Message.query.join(
        subquery, db.and_(Message.timestamp == subquery.c.max_timestamp,
                          db.or_(Message.sender_id == current_user.id, Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp.desc()
               ).paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.messages', page=last_messages.next_num) \
        if last_messages.has_next else None
    prev_url = url_for('main.messages', page=last_messages.prev_num) \
        if last_messages.has_prev else None
    return render_template('messages.html', messages=last_messages.items, next_url=next_url, prev_url=prev_url)


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])


@bp.route('/export_posts')
@login_required
def export_posts():
    if current_user.get_task_in_progress('export_posts'):
        flash(_('An export is in progress'))
    else:
        current_user.launch_task('export_posts', _('Exporting posts...'))
        db.session.commit()
    return redirect(url_for('main.user', username=current_user.username))


@bp.route('/load_comments/<int:post_id>', methods=['GET'])
def load_comments(post_id):
    post = Post.query.get(post_id)
    if post:
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.timestamp.asc()).offset(3).all()
        return jsonify([{'id': comment.id, 'author': comment.author.username, 'body': comment.body,
                         'timestamp': comment.timestamp,
                         'reactions': comment.first_reaction_emoji(),
                         'avatar': comment.author.avatar if comment.author.avatar is not None else comment.author.avatar_alt(30),
                         'hasReacted': current_user.has_reacted(comment.id, 'comment'),
                         'count_reactions': comment.count_reactions(comment.id),
                         } for comment in comments])

    else:
        return jsonify({'error': 'Post not found'}), 404


@bp.route('/user/<username>/media', methods=['POST', 'GET'])
@login_required
def media(username):
    user = get_user_from_username(username)
    images = user.images.all()
    popular_people, hashtag_counts, form = main_variables()
    return render_template('media.html', title=username, user=user, gallery=images, form=form,
                           hashtag_counts=hashtag_counts, popular_people=popular_people)


@bp.route('/user/<username>/liked')
@login_required
def liked(username):
    user = get_user_from_username(username)
    page = request.args.get('page', 1, type=int)
    popular_people, hashtag_counts, images, form = main_variables(user)
    posts = Post.query.join(Reaction, Reaction.post_id == Post.id).filter(
        Reaction.user_id == user.id, Post.user_id != user.id).order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    for post in posts.items:
        amount = post.comments.count()
        post.show_more_comments = amount > 3
    return render_template('user.html', title=username, user=user, popular_people=popular_people,
                           form=form, hashtag_counts=hashtag_counts, images=images, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        flash(_('File was not selected'))
        return redirect(request.url)

    file = request.files['image']
    if file.filename == '':
        flash(_('File was not selected'))
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Save the image to the database
        image = Image(filename=filename, user_id=current_user.id)
        db.session.add(image)
        db.session.commit()

        flash(_('Image uploaded successfully'))
        return redirect(url_for('main.media', username=current_user.username))


@bp.route('/react', methods=['POST'])
@login_required
def react():
    emoji = request.form.get('reaction')
    id = request.form.get('id')
    type = request.form.get('type')

    reaction = create_or_update_reaction(current_user.id, id, emoji, type)
    if type == "post":
        count_reactions = Post.count_reactions
    elif type == 'comment':
        count_reactions = Comment.count_reactions
    else:
        count_reactions = Image.count_reactions
    likes_total = count_reactions(id)

    if reaction is None:
        return jsonify({'emoji': 'empty', 'likes_total': likes_total})
    else:
        return jsonify({'emoji': emoji, 'likes_total': likes_total})

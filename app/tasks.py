import time
import json
import sys
from flask import render_template
from rq import get_current_job
from app import create_app, db
from app.models import Task, User, Post
from app.email import send_email

app = create_app()
app.app_context().push()


def _set_task_progress(progress):
    """
    Sets the progress of the current task.

    Args:
        progress (int): The progress of the task, expressed as a percentage.
    """
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progress', {'task_id': job.get_id(),
                                                     'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()


def export_posts(user_id):
    """
    Exports a user's posts to a JSON file and sends it to the user via email.

    Args:
        user_id (int): The ID of the user whose posts are to be exported.
    """
    try:
        user = User.query.get(user_id)
        _set_task_progress(0)
        data = []
        i = 0
        total_posts = user.posts.count()
        for post in user.posts.order_by(Post.timestamp.asc()):
            data.append({'body': post.body,
                         'timestamp': post.timestamp.isoformat() + 'Z'})
            time.sleep(5)
            i += 1
            _set_task_progress(100 * i // total_posts)

        # Send the email with the JSON file as an attachment
        send_email('[Muse_me] Your posts',
                   from_email=app.config['SENDGRID_EMAIL'],
                   to=[user.email],
                   html_content=render_template('email/export_posts.html', user=user),
                   attachments=[('posts.json', json.dumps({'posts': data}, indent=4), 'application/json')])
    except:
        # Log the error and set the task progress to 100% to indicate that the task failed
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())

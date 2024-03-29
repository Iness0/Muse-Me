from app import create_app, db, cli
from app.models import User, Post, Notification, Message, Task, Reaction

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post,
            'Notification': Notification, 'Message': Message, 'Reaction': Reaction, 'Task': Task}


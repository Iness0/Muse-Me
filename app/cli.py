import os
import click


def register(app):
    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    def update():
        """Updates .po files."""
        if os.system('pybabel extract -F babel.cfg -k _1 -o messages.pot .'):
            raise RuntimeError('Extract command failed')
        if os.system('pybabel update -i messages.pot -d app/translations'):
            raise RuntimeError('Update command failed')
        os.remove('messages.pot')

    @translate.command()
    def compile():
        """Compile different language files"""
        if os.system('pybabel compile -d app/translations'):
            raise RuntimeError('Compile command failed')

    @translate.command()
    @click.argument('lang')
    def init(lang):
        """Initialize new language"""
        if os.system('pybabel extract -F babel.cfg -k _1 -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system(
                'pybabel init -i messages.pot -d app/translations -l ' + lang):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')

import os
from wedding.app import create_app, db

from flask_migrate import Migrate
import click

options = {
    "swagger_ui": os.environ.get("WEDDING_SWAGGER_UI", False)
}

app = create_app(os.environ.get("WEDDING_CONFIG", "prod").lower(), options)
Migrate(app, db)

@app.cli.command()
@click.option("-f", "--firstname", prompt=True)
@click.option("-l", "--lastname", prompt=True)
@click.option("-e", "--email", prompt=True)
@click.password_option()
def create_admin(firstname, lastname, email, password):
    """Create an admin user."""
    from wedding.models import User
    from datetime import datetime
    today = datetime.utcnow()

    u = User.query.filter_by(email=email).first()
    if u is not None:
        click.secho(f"User with email {email} already exists. Exiting...", fg="red")
        return 1
    
    u = User()
    u.firstname = firstname
    u.lastname = lastname
    u.email = email
    u.password = password
    u.admin = True
    u.verified = True
    u.verified_on = today
    u.registered_on = today
    db.session.add(u)
    db.session.commit()

    click.secho(f"User '{email}' has been created, added as an admin and email has been flagged as registered. Please go ahead and login", fg="green")
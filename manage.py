from wedding.app import create_app, db
from wedding.models import *  # noqa

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

import os

app = create_app(os.environ.get("WEDDING_CONFIG", "dev"), options={})
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()

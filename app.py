import os
from wedding.app import create_app

app = create_app(os.environ.get("WEDDING_CONFIG", "dev"))
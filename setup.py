from setuptools import setup, find_packages

deps = [
    "flask",
    "sqlalchemy",
    "flask-sqlalchemy",
    "Flask-Migrate",
    'flask-script',
    'flask-bcrypt',
    "connexion",
    "pyjwt",
    "boto3"
]

setup(
    name="wedding-backend",
    version="v0.1.0",
    author="Sam Sherar <sbsherar@gmail.com>",
    packages=find_packages(),
    install_requires=deps,
)

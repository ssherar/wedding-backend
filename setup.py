from setuptools import setup, find_packages

deps = [
    "flask",
    "sqlalchemy",
    "flask-sqlalchemy",
    "Flask-Migrate",
    "flask-restplus",
    "pyjwt",
]

setup(
    name="wedding-backend",
    version="v0.0.1",
    author="Sam Sherar <sbsherar@gmail.com>",
    packages=find_packages(),
    install_requires=deps,
)

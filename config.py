import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
database_name = os.environ["DATABASE"]
database_username = os.environ["USERNAME"]
database_password = os.environ["PASSWORD"]

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = f"postgresql://{database_username}:{database_password}@localhost:5432/{database_name}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# WTF_CSRF_ENABLED = False

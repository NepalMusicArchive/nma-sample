from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail, Message
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import sqlite3
import io

# load environment file .env (local) or get environment variables for docker
load_dotenv()

# convert ENV Variables to localones
items_per_page = int(os.getenv("ITEMS_PER_PAGE"))
records_per_page =int(os.getenv("RECORDS_PER_PAGE"))
left_edge = int(os.getenv("LEFT_EDGE"))
right_edge = int(os.getenv("RIGHT_EDGE"))
left_current = int(os.getenv("LEFT_CURRENT"))
right_current = int(os.getenv("RIGHT_CURRENT"))
purge_backup_days = int(os.getenv("PURGE_BACKUP_DAYS"))
smtp_username = os.getenv("MAIL_USERNAME")
smtp_password = os.getenv("MAIL_PASSWORD")
max_idle_time = int(os.getenv("USER_SESSION_TIME"))
audio_length = int(os.getenv("AUDIO_LENGTH"))
server = os.getenv("NTFY_SERVER")
subscription = os.getenv("NTFY_SUBSCRITION")

# convert pagination variables into a list for easy transfer to pages
search_options = (left_edge, right_edge, left_current, right_current)

# set working dir for files
basedir = os.path.abspath(os.path.dirname((__file__)))

# initialize flask app
app = Flask(__name__)


@app.context_processor
def handle_context():
    return dict(os=os)


# initialize crypt library for passwords
bcrypt = Bcrypt(app)

# set working filepath for db
file_path = os.path.abspath(os.getcwd() + "db/nml.db")


# Variables for flask email
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_DEBUG"] = False
app.config["MAIL_USERNAME"] = smtp_username
app.config["MAIL_PASSWORD"] = smtp_password
app.config["MAIL_ASCII_ATTACHMENTS"] = True
app.config["MAIL_DEFAULT_SENDER"] = "app@nirat.com.np"
app.config["MAIL_SUPPRESS_SEND"] = False
app.config["MAIL_MAX_EMAILS"] = 5
app.config["UPLOAD_FOLDER"] = "/home/nirat/"

# security key for sqlalchemy queries
app.config["SECRET_KEY"] = "HArp33nu3mw0I91vQvAE"

# initialize DB and sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "db/nml.db"
)
# print (app.config["SQLALCHEMY_DATABASE_URI"])
app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = False

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@192.168.88.31:5432/nml'

# initialize DB and sqlalchemy
db = SQLAlchemy(app)
# initialize DB migrate
migrate = Migrate(app, db)

# initialize flask email
mail = Mail(app)

# initialize flask_login
login_manager = LoginManager(app)
logged_in_users = []

# import all routes
from nml import routes
from nml import library

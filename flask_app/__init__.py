from flask import Flask, render_template, redirect, session, request, flash, url_for
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
from uuid import uuid4
from flask_apscheduler import APScheduler
from dotenv import load_dotenv

load_dotenv()

import time
from flask_app.config.mysqlconnection import connectToMySQL
DATABASE = 'everyday_db'

# delete all comments
def comment_reset():
    query = "DELETE FROM comments;"
    return connectToMySQL(DATABASE).query_db(query)

# delete all posts
def post_reset():
    query = "DELETE FROM posts;"
    return connectToMySQL(DATABASE).query_db(query)

# delete all pictures of posts
def picture_reset():
    for file in os.listdir(POST_ABSOLUTE_PATH):
        os.remove(os.path.join(POST_ABSOLUTE_PATH, file))
        print(f'Picture {file} deleted')


app = Flask(__name__)
bcrypt = Bcrypt(app)

# initialize scheduler
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
# for interval task --> 'interval', id='do_job_1', seconds=10
@scheduler.task('cron', id='day_reset', hour="0")
def day_reset():
    comment_reset()
    time.sleep(2) #wait 2 seconds
    post_reset()
    time.sleep(2) #wait 2 seconds
    picture_reset()

scheduler.start()


#might need to change this when i deploy to the absolute path of server
POST_ABSOLUTE_PATH = '/Users/tonyaiello/Desktop/projects/everyday/flask_app/static/user_assets/post_images/'
AVATAR_ABSOLUTE_PATH = '/Users/tonyaiello/Desktop/projects/everyday/flask_app/static/user_assets/account_images/'
RELATIVE_PATH = '/Users/tonyaiello/Desktop/projects/everyday/flask_app/static/'

app.secret_key = getenv('SECRET_KEY')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# for file upload
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# make image names unique
def make_unique(string):
    ident = uuid4().__str__()
    return f"{ident}-{string}"
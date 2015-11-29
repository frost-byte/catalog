import os
from flask import Flask
app = Flask(__name__)

UPLOAD_FOLDER = "catalog/static/images"
ALLOWED_EXTENSIONS = ['png','jpg']
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')
APP_IMAGES = os.path.join(APP_STATIC, 'images')

app.config['APP_IMAGES'] = APP_IMAGES
app.config['APP_STATIC'] = APP_STATIC
app.config['APP_ROOT'] = APP_ROOT
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

import views
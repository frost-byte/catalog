import os
from flask import Flask
from flask.json import JSONEncoder

app = Flask(__name__)

# Custom JSONEncoder to handle nested objects and strings
# http://flask.pocoo.org/docs/0.10/api/#flask.json.JSONEncoder
# http://stackoverflow.com/a/21411576
class ModelsEncoder(JSONEncoder):
    def default(self, obj):

        if(isinstance(obj, basestring) == False):

            try:
                iterable = iter(obj)
            except TypeError:
                pass
            else:
                return list(iterable)

        return JSONEncoder.default(self, obj)


# App Configuration
# http://stackoverflow.com/a/14826195
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
app.json_encoder = ModelsEncoder

import views
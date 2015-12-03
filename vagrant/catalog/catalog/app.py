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
APP_CLIENT_SECRET = os.path.join(APP_ROOT, 'client_secret.json')
APP_DATABASE = "sqlite:///catalog/catalog.db"


app.config['APP_IMAGES'] = APP_IMAGES
app.config['APP_STATIC'] = APP_STATIC
app.config['APP_ROOT'] = APP_ROOT
app.config['APP_DATABASE'] = APP_DATABASE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
app.config['APP_CLIENT_SECRET'] = APP_CLIENT_SECRET
app.json_encoder = ModelsEncoder

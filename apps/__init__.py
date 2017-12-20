"""module to initialize the app"""
from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from apps import config

app = Flask(__name__)

config_name = config.DevelopmentConfig
app.config.from_object(config_name)
app.config['PAGINATION_PAGE_SIZE']=2
app.config['PAGINATION_PAGE_ARGUMENT_NAME']='page'

auth = HTTPBasicAuth()
db = SQLAlchemy(app)
ma = Marshmallow(app)


from apps.views import *

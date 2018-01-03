"""module to initialize the app"""
from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flasgger import Swagger
from apps import config

app = Flask(__name__)

Swagger(app)
config_name = config.DevelopmentConfig
app.config.from_object(config_name)
app.config['PAGINATION_PAGE_SIZE']=2
app.config['PAGINATION_PAGE_ARGUMENT_NAME']='page'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

auth = HTTPBasicAuth()
db = SQLAlchemy(app)
ma = Marshmallow(app)


from apps.views import *

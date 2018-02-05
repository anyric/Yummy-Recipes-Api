"""module to initialize the app"""
from flask import Flask, redirect
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_heroku import Heroku
from flasgger import Swagger

from apps.utilities import config

app = Flask(__name__)
config_name = config.DevelopmentConfig

app.config['SWAGGER'] = {"swagger": "2.0",
                             "title": "Yummy Recipes",
                             "uiversion": 2,
                             "info": {
                                "title": "Yummy Recipe API",
                                "description": "Yummy Recipe is an application that allow users to \
                                keep track of their owesome food recipes. It helps individuals who love to cook \
                                and eat good food to remember recipes and also share with others. <br /><br />\
                                Checkout on github: https://github.com/anyric/Yummy-Recipes-Api",
                                "version": "1.0.0",
                                "basepath": '/',
                             },
                             "securityDefinitions": {
                                "TokenHeader": {
                                    "type": "apiKey",
                                    "name": "x-access-token",
                                    "in": "header"
                                },
                             }}

app.config.from_object(config_name)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Swagger(app)
heroku = Heroku(app)
auth = HTTPBasicAuth()
db = SQLAlchemy(app)
ma = Marshmallow(app)


@app.errorhandler(404)
def pageNotFound(error):
    """function to handle internal server errors"""
    return jsonify({"message":"page not found!"}), 404

@app.errorhandler(405)
def wrongRequestMethod(error):
    """function to handle internal server errors"""
    return jsonify({"message":"wrong request method!"}), 405

@app.errorhandler(500)
def serverDown(error):
    """function to handle internal server errors"""
    return jsonify({"message":"server down!"}), 500
@app.route("/")
def index():
    return redirect("/apidocs/")

from apps.views.user_view import *
from apps.views.recipe_view import *
from apps.views.category_view import *

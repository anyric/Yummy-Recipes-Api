"""main module that runs the application"""
from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from controller import getuser, viewcategory
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/yummy-api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

auth = HTTPBasicAuth()
db = SQLAlchemy(app)


@auth.get_password
def get_password(username):
    """function to get user password"""
    user = getuser(username)
    if user:
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    """function to display error message to users """
    return make_response(jsonify({'error': 'Unauthorized access'}), 404)

@app.route('/recipe/api/v1.0/category', methods=['GET'])
@auth.login_required
def get_category():
    """function to query recipe category of a user"""
    user = getuser(auth.username())
    category = viewcategory(user.user_id)
    return jsonify({'category': category})



if __name__ == '__main__':
    app.run()

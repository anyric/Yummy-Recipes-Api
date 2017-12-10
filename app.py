"""main module that runs the application"""
from flask import Flask, jsonify, request, url_for, abort, g, render_template, make_response, json
from flask_sqlalchemy import SQLAlchemy
from user import User
from category import Category
from recipe import Recipe
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/yummy-api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

auth = HTTPBasicAuth()
db = SQLAlchemy(app)


@app.route('/recipe/api/v1.0/user', methods = ['POST'])
def new_user():
    """function to create new user"""
    firstname = request.json.get('firstname', "")
    lastname = request.json.get('lastname', "")
    username = request.json.get('username', "")
    password = request.json.get('password', "")

    if firstname.strip() and lastname.strip() and username.strip() and password.strip():
        createuser(firstname, lastname, username, password)

    user = getuser(username)
    return jsonify({'username': user.username})


@auth.verify_password
def verify_password(username, password):
    """function to verify username and password"""
    user = getuser(username)
    if not user or not user.password == password:
        return False
    g.user = user
    return True

@app.errorhandler(404)
def not_found(error):
    """function to format error response"""
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/recipe/api/v1.0/category', methods=['POST'])
@auth.login_required
def new_category():
    """function to create new recipe category of a user"""
    category_name = request.json.get('name')
    description = request.json.get('description')
    user_id = g.user.id

    if category_name.strip() and description.strip():

        createcategory(user_id, category_name, description)
        category = viewcategory(user_id)

    return jsonify({'category': dict(category_name=category)})


@app.route('/recipe/api/v1.0/category', methods=['PUT'])
@auth.login_required
def update_category():
    """function to update recipe category of a user"""
    category_old_name = request.json.get('old_name')
    category_new_name = request.json.get('new_name')
    description = request.json.get('description')
    user_id = g.user.id

    if category_old_name.strip() and category_old_name.strip() and description.strip():
        category = getcategory(category_old_name)
        updatecategory(category, category_new_name, description)
        category = viewcategory(user_id)

    return jsonify({'category': dict(category_name=category)})

@app.route('/recipe/api/v1.0/category', methods=['GET'])
@auth.login_required
def view_category():
    """function to query recipe category of a user"""
    user = getuser(g.user.username)
    category = viewcategory(user.id)
    return jsonify({'category': dict(category_name=category)})

@app.route('/recipe/api/v1.0/category', methods=['DELETE'])
@auth.login_required
def delete_category():
    """function to delete recipe category of a user"""
    category_name = request.json.get('categoryname')
    if category_name is not None:
        deletecategory(category_name)
    else:
        abort(404)

    user = getuser(g.user.username)
    category = viewcategory(user.user.id)
    return jsonify({'category': dict(category_name=category)})


@app.route('/recipe/api/v1.0/recipe', methods=['POST'])
@auth.login_required
def new_recipe():
    """function to create new recipe of a user"""
    recipe_name = request.json.get('name')
    description = request.json.get('description')
    user_id = g.user.user_id

    if recipe_name.strip() and description.strip():
        createrecipe(user_id, recipe_name, description)
        recipe = viewrecipe(user_id)

    return jsonify({'recipe': dict(recipe_name=recipe)})

@app.route('/recipe/api/v1.0/recipe', methods=['PUT'])
@auth.login_required
def update_recipe():
    """function to update recipe of a user"""
    recipe_old_name = request.json.get('old_name')
    recipe_new_name = request.json.get('new_name')
    description = request.json.get('description')
    user_id = g.user.id

    if recipe_old_name.strip() and recipe_new_name.strip() and description.strip():
        recipe = getcategory(recipe_old_name)
        updaterecipe(recipe, recipe_new_name, description)
        recipe = viewrecipe(user_id)

    return jsonify({'recipe': dict(recipe_name=recipe)})

@app.route('/recipe/api/v1.0/recipes', methods=['GET'])
@auth.login_required
def view_recipe():
    """function to recipe category of a user"""
    user = getuser(g.user.username)
    recipe = viewrecipe(user.user_id)
    return jsonify({'recipe': dict(recipe_name=recipe)})


@app.route('/recipe/api/v1.0/recipe', methods=['DELETE'])
@auth.login_required
def delete_recipe():
    """function to delete recipe of a user"""
    recipe_name = request.json.get('recipename')
    if recipe_name is not None:
        deleterecipe(recipe_name)
    else:
        abort(404)

    user = getuser(g.user.username)
    recipe = viewrecipe(user.user.id)
    return jsonify({'recipe': dict(recipe_name=recipe)})


if __name__ == '__main__':
    app.run()

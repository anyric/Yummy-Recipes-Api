"""main module that runs the application"""
from flask import Flask, jsonify, request, url_for, abort, g
from flask_sqlalchemy import SQLAlchemy
from controller import createuser, getuser, createcategory, getcategory, updatecategory, viewcategory, deletecategory, createrecipe, viewrecipe, getrecipe, updaterecipe, deleterecipe
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

    if username is None or password is None:
        abort(400)
    if getuser(username) is not None:
        abort(400)

    createuser(firstname, lastname, username, password)
    user = getuser(username)

    return jsonify({'username': user.username}), 201, {'Location': url_for('get_user', id=user.id, _external=True)}


@auth.verify_password
def verify_password(username, password):
    """function to verify username and password"""
    user = getuser(username)
    if not user or not user.password == password:
        return False
    g.user = user
    return True


@app.route('/recipe/api/v1.0/category', methods=['POST'])
@auth.login_required
def new_category():
    """function to create new recipe category of a user"""
    category_name = request.json.get('name')
    description = request.json.get('description')
    user_id = g.user.user_id

    if category_name is None or description is None:
        abort(400)

    category = getcategory(category_name)
    if category is not None:
        updatecategory(category, category_name, description)
        category = viewcategory(user_id)
    else:
        createcategory(user_id, category_name, description)
        category = viewcategory(user_id)

    return jsonify({'category': category}), 201, {'Location': url_for('view_category', id=category.id, _external=True)}


@app.route('/recipe/api/v1.0/categories', methods=['GET'])
@auth.login_required
def view_category():
    """function to query recipe category of a user"""
    user = getuser(g.user.username)
    category = viewcategory(user.user_id)
    return jsonify({'category': category})


@app.route('/recipe/api/v1.0/categoryname', methods=['POST'])
@auth.login_required
def delete_category():
    """function to delete recipe category of a user"""
    category_name = request.json.get('categoryname')
    deleterecipe(category_name)

    user = getuser(g.user.username)
    category = viewcategory(user.user_id)
    return jsonify({'category': category})


@app.route('/recipe/api/v1.0/recipe', methods=['POST'])
@auth.login_required
def new_recipe():
    """function to create new recipe of a user"""
    recipe_name = request.json.get('name')
    description = request.json.get('description')
    user_id = g.user.user_id

    if recipe_name is None or description is None:
        abort(400)

    recipe = getrecipe(recipe_name)
    if recipe is not None:
        updaterecipe(recipe, recipe_name, description)
        recipe = viewrecipe(user_id)

    else:
        createrecipe(user_id, recipe_name, description)
        recipe = viewrecipe(user_id)

    return jsonify({'recipe': recipe}), 201, {'Location': url_for('view_recipe', id=recipe.id, _external=True)}


@app.route('/recipe/api/v1.0/recipes', methods=['GET'])
@auth.login_required
def view_recipe():
    """function to recipe category of a user"""
    user = getuser(g.user.username)
    recipe = viewrecipe(user.user_id)
    return jsonify({'recipe': recipe})


@app.route('/recipe/api/v1.0/recipename', methods=['POST'])
@auth.login_required
def delete_recipe():
    """function to delete recipe of a user"""
    recipe_name = request.json.get('recipename')
    deleterecipe(recipe_name)

    user = getuser(g.user.username)
    recipe = viewrecipe(user.user_id)
    return jsonify({'recipe': recipe})


if __name__ == '__main__':
    app.run()

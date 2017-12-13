"""main module that runs the application"""
from datetime import datetime
from apps import app, auth
from flask import request, abort, jsonify, g, make_response
from apps.user import Users
from apps.category import Category
from apps.recipe import Recipe

@app.route('/recipe/api/v1.0/user', methods=['POST'])
def new_user():
    """function to create new user"""
    firstname = str(request.json.get('firstname', "")).strip()
    lastname = str(request.json.get('lastname', "")).strip()
    username = str(request.json.get('username', "")).strip()
    password = str(request.json.get('password', "")).strip()

    if firstname and lastname and username and password:
        user = Users(firstname, lastname, username, password)
        user.save()
    return jsonify({'username': user.username})


@app.route('/recipe/api/v1.0/user', methods=['GET'])
def view_users():
    """function to query users list"""
    userlist = Users.getusers()

    response = jsonify(userlist)
    response.status_code = 200

    return response


@auth.verify_password
def verify_password(username, password):
    """function to verify username and password"""
    user = Users.query.filter_by(username=username).first()

    if not user or not user.password == password:
        return False
    g.user = user
    return True

@app.errorhandler(404)
def not_found():
    """function to format error response"""
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/recipe/api/v1.0/category', methods=['POST'])
@auth.login_required
def new_category():
    """function to create new recipe category of a user"""
    category_name = str(request.json.get('name', '')).strip()
    description = str(request.json.get('description', '')).strip()
    user_id = g.user.id
    date_modified = datetime.utcnow()

    if category_name and description:

        category = Category(user_id, category_name, description, date_modified)
        category.save()

        response = jsonify({"message":"category {} was added successfully!".format(category.name) })
        response.status_code = 201
    else:
        response = jsonify({"message":"Please enter all details!"})
        response.status_code = 200

    return response


@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['PUT'])
@auth.login_required
def update_category(category_id):
    """function to update recipe category of a user"""

    category_name = str(request.json.get('name', '')).strip()
    description = str(request.json.get('description', '')).strip()

    category = Category.query.filter_by(id=category_id).first()

    if not category:
        abort(404)

    elif category_name and description:

        category.name = category_name
        category.description = description
        category.save()
        
        response = jsonify({"message": "category {} was updated successfully".format(category.id)})
        response.status_code = 201
    else:
        response = jsonify({"message": "Please enter new details!"})
        response.status_code = 200

    return response

@app.route('/recipe/api/v1.0/category', methods=['GET'])
@auth.login_required
def view_category():
    """function to query recipe category of a user"""
    user = Users.query.filter_by(username=g.user.username).first()

    categorylists = Category.getcategory(user.id)
    if categorylists is not None:
        response = jsonify(categorylists)
        response.status_code = 200
    else:
        response = jsonify({"message": "No category added yet!"})
        response.status_code = 200

    return response


@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['DELETE'])
@auth.login_required
def delete_category(category_id):
    """function to delete recipe category of a user"""
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        abort(404)
    else:
        category.delete()
        response = jsonify({"message": "category {} was deleted successfully".format(category.name)})
        response.status_code = 200
        return response


@app.route('/recipe/api/v1.0/recipe', methods=['POST'])
@auth.login_required
def new_recipe():
    """function to create new recipe of a user"""
    recipe_name = str(request.json.get('name', '')).strip()
    incredients = str(request.json.get('incredients', '')).strip()
    category_id = int(request.json.get('category_id', ''))
    date_modified = datetime.utcnow()

    if recipe_name and incredients and category_id > 0:
        recipe = Recipe(category_id, recipe_name, incredients, date_modified)
        recipe.save()
        response = jsonify({"message": "recipe {} was added successfully!".format(recipe.name)})
        response.status_code = 201
    else:
        response = {"message":"Please enter all details!"}, 200
    return response


@app.route('/recipe/api/v1.0/recipe/<int:recipe_id>', methods=['PUT'])
@auth.login_required
def update_recipe(recipe_id):
    """function to update recipe of a user"""
    recipe_name = str(request.json.get('name', '')).strip()
    ingredients = str(request.json.get('ingredients', '')).strip()

    recipe = Recipe.query.filter_by(id=recipe_id).first()

    if recipe is not None:
        recipe.name = recipe_name
        recipe.ingredients = ingredients
        recipe.save()
        response = jsonify({"message": "recipe {} was updated successfully!".format(recipe.id)})
        response.status_code = 201
    else:
        response = {"message": "No recipes added yet!"}, 200

    return response

@app.route('/recipe/api/v1.0/recipe/<int:category_id>', methods=['GET'])
@auth.login_required
def view_recipe(category_id):
    """function to recipe category of a user"""
    recipelists = Recipe.getrecipe(category_id)

    if recipelists:
        response = jsonify(recipelists)
        response.status_code = 200
    else:
        response = {"message": "No recipes added yet!"}, 200

    return response


@app.route('/recipe/api/v1.0/recipe/<int:recipe_id>', methods=['DELETE'])
@auth.login_required
def delete_recipe(recipe_id):
    """function to delete recipe of a user"""
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if not recipe:
        abort(404)
    else:
        recipe.delete()
        response = {"message": "recipe {} deleted successfully!".format(recipe_id)}, 200
    return response

if __name__ == '__main__':
    app.run()

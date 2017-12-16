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
        user_exit = Users.query.filter_by(username=username).first()
        if user_exit:
            response = jsonify({"message":"username {} already exits!".format(username)}, 200)
        else:
            user = Users(firstname, lastname, username, password)
            user.save()
            response = jsonify({'message': "user {} registered successfully!".format(user.username)}, 201)
    return response


@app.route('/recipe/api/v1.0/user', methods=['GET'])
def view_users():
    """function to query users list"""
    userlist = Users.getusers()

    response = jsonify(userlist, 200)

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
    #date_modified = datetime.utcnow()

    if category_name and description:
        cat_exits = Category.query.filter_by(name=category_name).first()

        if cat_exits:
            response = jsonify({"message":"Category {} already exits".format(category_name)}, 200)
        else:

            category = Category(user_id, category_name, description)
            category.save()

            response = jsonify({"message":"category {} was added successfully!".format(category.name)}, 201)
    else:
        response = jsonify({"message":"Please enter all details!"}, 200)

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
        category.date_modified = datetime.utcnow()
        category.save()

        response = jsonify({"message": "category {} was updated successfully".format(category.id)}, 201)
    else:
        response = jsonify({"message": "Please enter new details!"}, 200)


    return response

@app.route('/recipe/api/v1.0/category', methods=['GET'])
@auth.login_required
def view_category():
    """function to query recipe category of a user"""
    user = Users.query.filter_by(username=g.user.username).first()

    categorylist = Category.query.filter_by(user_id=user.id).all()
    results = []
    if categorylist is not None:
        for category in categorylist:
            obj = {
                'id': category.id,
                'name': category.name,
                'user': category.user_id,
                'description': category.description,
                'date_modified':category.date_modified
                }
            results.append(obj)
            response = jsonify(results, 200)

    else:
        response = jsonify({"message": "No category added yet!"}, 200)


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
        response = jsonify({"message": "category {} was deleted successfully".format(category.name)}, 200)

        return response


@app.route('/recipe/api/v1.0/recipe', methods=['POST'])
@auth.login_required
def new_recipe():
    """function to create new recipe of a user"""
    recipe_name = str(request.json.get('name', '')).strip()
    ingredients = str(request.json.get('ingredients', '')).strip()
    category_id = int(request.json.get('category_id', ''))
    #date_modified = datetime.utcnow()

    if recipe_name and ingredients and category_id > 0:
        recipe = Recipe.query.filter_by(name=recipe_name).first()
        if not recipe:

            recipe = Recipe(category_id, recipe_name, ingredients)
            recipe.save()
            response = jsonify({"message": "recipe {} was added successfully!".format(recipe.name)})
            response.status_code = 201
        else:
            response = jsonify({"message":"Recipe name already exits"}, 200)
    else:
        response = jsonify({"message":"Please enter all details!"}, 200)
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
        recipe.date_modified = datetime.utcnow()
        recipe.save()
        response = jsonify({"message": "recipe {} was updated successfully!".format(recipe.id)})
        response.status_code = 201
    else:
        response = jsonify({"message": "No recipes added yet!"}, 200)

    return response

@app.route('/recipe/api/v1.0/recipe/<int:category_id>', methods=['GET'])
@auth.login_required
def view_recipe(category_id):
    """function to recipe category of a user"""
    recipelists = Recipe.query.filter_by(category_id=category_id).all()
    results = []
    if recipelists:
        for recipe in recipelists:
            obj = {
                'id': recipe.id,
                'name': recipe.name,
                'category': recipe.category_id,
                'ingredients': recipe.ingredients,
                'date_modified':recipe.date_modified
                }
            results.append(obj)
        response = jsonify(results)
        response.status_code = 200
    else:
        response = jsonify({"message": "No recipes added yet!"}, 200)

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
        response = jsonify({"message": "recipe {} deleted successfully!".format(recipe_id)}, 200)
    return response

if __name__ == '__main__':
    app.run()

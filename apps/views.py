"""main module that runs the application"""
from apps import app, auth
from flask import request, abort, jsonify, g
from apps.user import Users
from apps.category import Category
from apps.recipe import Recipe

@app.route('/recipe/api/v1.0/user', methods=['POST'])
def new_user():
    """function to create new user"""
    firstname = request.json.get('firstname', "")
    lastname = request.json.get('lastname', "")
    username = request.json.get('username', "")
    password = request.json.get('password', "")

    if firstname.strip() and lastname.strip() and username.strip() and password.strip():
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
        print("******************")
        print(user.password)
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
    category_name = request.json.get('name')
    description = request.json.get('description')
    user_id = g.user.id

    if category_name.strip() and description.strip():

        category = Category(user_id, category_name, description)
        category.save()

    response = jsonify(category)
    response.status_code = 201

    return response


@app.route('/recipe/api/v1.0/category/', methods=['PUT'])
@auth.login_required
def update_category():
    """function to update recipe category of a user"""
    category_old_name = request.json.get('old_name')
    category_new_name = request.json.get('new_name')
    description = request.json.get('description')
    user_id = g.user.id

    if category_old_name.strip() and category_new_name.strip() and description.strip():
        category = Category.query.filter_by(name=category_old_name).first()

        category.name = category_new_name
        category.description = description
        category.save()
        
        #categorylists = Category.getcategory(user.id)
        response = jsonify(category)
        response.status_code = 201

    return response

@app.route('/recipe/api/v1.0/category', methods=['GET'])
@auth.login_required
def view_category():
    """function to query recipe category of a user"""
    user = Users.query.filter_by(username=g.user.username).first()

    categorylists = Category.getcategory(user.id)
    response = jsonify(categorylists)
    response.status_code = 200

    return response


@app.route('/recipe/api/v1.0/category/', methods=['DELETE'])
@auth.login_required
def delete_category():
    """function to delete recipe category of a user"""
    category_name = request.json.get('categoryname')
    if category_name is not None:
        category = Category.query.filter_by(name=category_name).first()
        category.delete()
    else:
        abort(404)

    response = {"message": "category {} deleted successfully".format(category_name)}, 200
    return response


@app.route('/recipe/api/v1.0/recipe', methods=['POST'])
@auth.login_required
def new_recipe():
    """function to create new recipe of a user"""
    recipe_name = request.json.get('name')
    description = request.json.get('description')
    category_id = request.json.get('category_id')

    if recipe_name.strip() and description.strip():
        recipe = Recipe(category_id, recipe_name, description)
        recipe.save()

    recipelists = Recipe.getrecipe()
    results = []
    for recipelist in recipelists:
        if recipelist.category_id == category_id:
            results.append(recipelist)

    response = jsonify({'recipe': dict(recipe_name=results)})
    response.status_code = 201

    return response


@app.route('/recipe/api/v1.0/recipe', methods=['PUT'])
@auth.login_required
def update_recipe():
    """function to update recipe of a user"""
    recipe_old_name = request.json.get('old_name')
    recipe_new_name = request.json.get('new_name')
    description = request.json.get('description')
    category_id = request.json.get('category_id')

    if recipe_old_name.strip() and recipe_new_name.strip() and description.strip():
        recipe = Recipe.query.filter_by(name=recipe_old_name).first()

        recipe.name = recipe_new_name
        recipe.description = description
        recipe.save()

        recipelists = Recipe.getrecipe()
        results = []
        for recipelist in recipelists:
            if recipelist.category_id == category_id:
                results.append(recipelist)

    response = jsonify({'recipe': dict(recipe_name=results)})
    response.status_code = 200

    return response

@app.route('/recipe/api/v1.0/recipes', methods=['GET'])
@auth.login_required
def view_recipe():
    """function to recipe category of a user"""

    recipelists = Recipe.getrecipe()

    response = jsonify({'recipe': dict(recipe_name=recipelists)})
    response.status_code = 200

    return response


@app.route('/recipe/api/v1.0/recipe', methods=['DELETE'])
@auth.login_required
def delete_recipe():
    """function to delete recipe of a user"""
    recipe_name = request.json.get('recipename')
    if recipe_name is not None:
        recipe = Recipe.query.filter_by(name=recipe_name).first()
        recipe.delete()

    else:
        abort(404)

    response = {"message": "recipe {} deleted successfully".format(recipe.id)}, 200
    return response

if __name__ == '__main__':
    app.run()

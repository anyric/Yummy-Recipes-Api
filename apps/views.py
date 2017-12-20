"""main module that runs the application"""
from datetime import datetime, timedelta
import jwt
from apps import app, auth
from flask import request, abort, jsonify, g, make_response, json
from apps.user import Users
from apps.category import Category, CategorySchema
from apps.recipe import Recipe, RecipeSchema
from apps.config import Config
from apps.json import json
from apps.paginate import PaginationHelper

category_schema = CategorySchema()
category_schema = CategorySchema(many=True)

recipe_schema = RecipeSchema()
recipe_schema = RecipeSchema(many=True)

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
            response = jsonify({"message":"username {} already exits!".format(username)}, 202)
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


@app.route('/recipe/api/v1.0/user/login', methods=['POST'])
def login_user():
    """function to verify username and password"""
    username = request.json.get('username', '')
    password = request.json.get('password', '')

    user = Users.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message":"could not verify 1"}, 401)
        # return make_response('Could not verify', 401,
        #                      {'WWW-Authenticate':
        #                       'Basic realm="Login Required!"'})

    if user.password == password:
        token = jwt.encode({'public_id': user.id,
                            'exp': datetime.utcnow() + timedelta(hours=8)}, Config.SECRET)

        return jsonify({'token': token.decode('UTF-8'),
                        'message': 'Login successful!'}), 200
    return jsonify({"message":"could not verify 2"}, 401)
    # return make_response('Could not verify', 401,
    #                      {'WWW-Authenticate':
    #                       'Basic realm="Login Required!"'})

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

@app.route('/recipe/api/v1.0/category/', methods=['GET'])
@auth.login_required
def view_category():
    """function to query paginated recipe category of a user"""
    user = Users.query.filter_by(id=g.user.id).first()
    pagination_helper = PaginationHelper(
        request,
        query=Category.query.filter(Category.user_id == user.id),
        resource_for_url='view_category',
        key_name='results',
        schema=category_schema)
        
    search = request.args.get('q')

    if search:
        pagination_helper = PaginationHelper(
        request,
        query=Category.query.filter(Category.user_id == user.id, Category.name.contains(search)),
        resource_for_url='view_category',
        key_name='results',
        schema=category_schema)
        result = pagination_helper.paginate_query()
        return jsonify({'categories':result})
    result = pagination_helper.paginate_query()
    return jsonify({'categories':result})


@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['GET'])
@auth.login_required
def view_category_by(category_id):
    """function to query a recipe category of a user by category id"""
    user = Users.query.filter_by(id=g.user.id).first()
    categorylists = Category.query.filter_by(id=category_id).first()

    if categorylists is None:
        response = jsonify({"Message": "No category with id {} \
was found!".format(category_id)}, 200)
        return response

    results = []

    if user.id == categorylists.user_id:

        if categorylists:
            for category in categorylists:
                obj = {
                    'id': category.id,
                    'name': category.name,
                    'user': category.user_id,
                    'description': category.description,
                    'date_modified':category.date_modified
                    }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
    else:
        response = jsonify({"Message": "You don't have the right \
to view that category"}, 200)
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
        response = jsonify({"message": "category {} was \
                            deleted successfully".format(category.name)}, 200)

        return response


@app.route('/recipe/api/v1.0/recipe', methods=['POST'])
@auth.login_required
def new_recipe():
    """function to create new recipe of a user"""
    recipe_name = str(request.json.get('name', '')).strip()
    ingredients = str(request.json.get('ingredients', '')).strip()
    category_id = int(request.json.get('category_id', ''))


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


# @app.route('/recipe/api/v1.0/recipe/<int:recipe_id>', methods=['GET'])
# @auth.login_required
# def view_recipe_by(recipe_id):
#     """function to query a recipe of a user by recipe id"""
#     recipelists = Recipe.query.filter_by(id=recipe_id)

#     if recipelists is None:
#         response = jsonify({"Message": "No recipe with id {} was found!".format(recipe_id)}, 200)
#         return response

#     results = []
#     if recipelists:
#         for recipe in recipelists:
#             obj = {
#                 'id': recipe.id,
#                 'name': recipe.name,
#                 'categroy_id': recipe.category_id,
#                 'ingredients': recipe.ingredients,
#                 'date_modified':recipe.date_modified
#                 }
#             results.append(obj)
#         response = jsonify(results)
#         response.status_code = 200
#     else:
#         response = jsonify({"message": "No recipe with id {} found!".format(recipe_id)}, 200)

#     return response


@app.route('/recipe/api/v1.0/category/<int:category_id>/recipes/', methods=['GET'])
@auth.login_required
def view_recipe_in_category(category_id):
    """function to view paginated recipe of a user"""
    user = Users.query.filter_by(id=g.user.id).first()
    print(user.id)
    print("****************")
    # categorylist = Category.query.filter(Category.id == category_id, Category.user_id == user.id)
    categorylist = Category.query.get_or_404(category_id)
    recipes = Recipe.query.filter_by(category_id=categorylist.id).first()
    print(categorylist, "@@@@@@@@@@@@@@@@@@@@@@@")

    if categorylist is None:
        return jsonify({"Message":"No category found!"}, 200)

    # if user.id == categorylist.user_id:
    if recipes:
        pagination_helper = PaginationHelper(
            request,
            query=Recipe.query.filter(Recipe.category_id==category_id),
            resource_for_url='view_recipe_in_category',
            key_name='results',
            schema=recipe_schema)
        result = pagination_helper.paginate_query()
        return jsonify({'recipes':result}, 201)
        # else:
        #     return jsonify({"Message":"No category with id {} was found!".format(category_id)}, 200)
    else:
        return jsonify({"Message":"You don't have right to view the recipe list!"}, 200)

    return jsonify({"Message": "No records found!"}, 200)

@app.route('/recipe/api/v1.0/category/<int:category_id>/recipes/<int:recipe_id>', methods=['GET'])
@auth.login_required
def view_recipe_by_id(category_id, recipe_id):
    """function to query a recipe category of a user by category id"""

    user = Users.query.filter_by(id=g.user.id).first()
    categorylists = Category.query.filter(Category.user_id == user.id, Category.id == category_id).first()
    recipes = Recipe.query.filter(Recipe.id == recipe_id, Recipe.category_id == category_id)


    if categorylists is None:
        response = jsonify({"Message": "No category with id {} \
was found!".format(category_id)}, 200)
        return response

    if recipes is None:

        response = jsonify({"Message": "No recipe with id {} \
was found!".format(recipe_id)}, 200)
        return response

    results = []

    if user.id == categorylists.user_id:

        if recipes:
            for recipe in recipes:
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

            return response
    else:
        response = jsonify({"Message": "You don't have the right \
to view that recipe"}, 200)
        return response
    return jsonify({"Message":"No records found!"})


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

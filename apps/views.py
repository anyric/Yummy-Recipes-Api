"""main module that runs the application"""
from datetime import datetime
from flask import request, jsonify, g, make_response, json
import jwt
from apps import app, auth
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
def register_new_user():
    """function to create new user
    ---
    tags:
      - users
    parameters:
      - in: body
        name: body
        description: a dictionary containing user details
        required: true
    responses:
      201:
        description: New user added successfully!
      202:
        description: Username already exist!
    """

    firstname = str(request.json.get('firstname', "")).strip()
    lastname = str(request.json.get('lastname', "")).strip()
    username = str(request.json.get('username', "")).strip()
    password = str(request.json.get('password', "")).strip()

    if firstname and lastname and username and password:
        if firstname.isalpha() and lastname.isalpha() and username.isalpha():
            if password.isalpha():
                return jsonify({"Message":"Password can't be only alphabets"}), 400

            user_exit = Users.query.filter_by(username=username).first()
            if user_exit:
                return jsonify({"message":"username {} already exits!".format(username)}), 400
            else:
                user = Users(firstname, lastname, username, password)
                user.save()
                response = jsonify({'message': "user {} registered successfully!".format(user.username)}), 201
                return response
        else:
            return jsonify({"Message":"Only password can contain none alphabet character"}), 400

    return jsonify({"Message":"Please fill in all fields"}), 400


@app.route('/recipe/api/v1.0/user', methods=['GET'])
def view_users():
    """function to query users list
    ---
    tags:
      - users
    responses:
      200:
        description: Ok
    """
    userlist = Users.getusers()

    if not userlist:
        return jsonify({"Message":"No registered user found!"}), 204
    else:
        return jsonify(userlist), 200


@auth.verify_password
def verify_password(username, password):
    """function to verify username and password"""
    user = Users.query.filter_by(username=username).first()

    if not user or not user.password == password:
        return False
    g.user = user
    return True

@app.route('/recipe/api/v1.0/category', methods=['POST'])
@auth.login_required
def create_new_category():
    """function to create new recipe category of a user
    ---
    tags:
      - categories
    parameters:
      - in: body
        name: body
        description: a json object containing details of a category to be added
        required: true
    responses:
      200:
        description: Ok
    """
    category_name = str(request.json.get('name', '')).strip()
    description = str(request.json.get('description', '')).strip()
    user_id = g.user.id

    if category_name and description:
        cat_exits = Category.query.filter_by(name=category_name).first()

        if cat_exits:
            return jsonify({"message":"Category {} already exits".format(category_name)}), 400
        else:
            category = Category(user_id, category_name, description)
            category.save()

            return jsonify({"message":"category {} was added successfully!".format(category.name)}), 201
    else:
        return jsonify({"message":"Please enter all details!"}), 400


@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['PUT'])
@auth.login_required
def update_category(category_id):
    """function to update category for a user
    ---
    tags:
      - categories
    parameters:
      - in: path
        name: category_id
        description: Id of a category
        required: true
      - in: body
        name: body
        description: a json object containing details of a category to be added
        required: true
    responses:
      200:
        description: Ok
    """

    category_name = str(request.json.get('name', '')).strip()
    description = str(request.json.get('description', '')).strip()

    category = Category.query.filter_by(id=category_id).first()

    if not category:
        return jsonify({"Message":"No category with id {} was found!".format(category_id)}), 400

    if category_name and description:

        category.name = category_name
        category.description = description
        category.date_modified = datetime.utcnow()
        category.save()
        return jsonify({"Message": "category {} was updated successfully".format(category.id)}), 201
    else:
        return jsonify({"Message": "Please enter new details!"}), 400


@app.route('/recipe/api/v1.0/category/', methods=['GET'])
@auth.login_required
def view_category():
    """
    function to query paginated recipe category of a user
    ---
    tags:
      - categories
    responses:
      200:
        description: Ok
    """
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
        if result['count']:
            return jsonify({'categories':result}), 200
        else:
            return jsonify({'Message':"No record matches search term"}), 204

    result = pagination_helper.paginate_query()
    if result['count']:
        return jsonify({'categories':result}), 200
    print("am finished")
    return jsonify({"Message":"No record found"}), 404


@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['GET'])
@auth.login_required
def view_category_by_id(category_id):
    """function to query a recipe category of a user by category id
    ---
    tags:
      - categories
    parameters:
      - in: path
        name: category_id
        description: Id of a category
        required: true
    responses:
      200:
        description: Ok
    """
    if category_id > 0:
        user = Users.query.filter_by(id=g.user.id).first()
        categorylists = Category.query.filter(Category.id == category_id, Category.user_id == user.id).first()

        if not categorylists:
            response = jsonify({"Message": "No category with id {} was found!".format(category_id)}), 204# no content found
            return response

        results = {}

        if user.id == categorylists.user_id:

            if categorylists:
                results["id"] = categorylists.id
                results["name"] = categorylists.name
                results["user"] = categorylists.user_id
                results["description"] = categorylists.description
                results["date_modified"] = categorylists.date_modified

                response = jsonify(results), 200
                return response

    return jsonify({"Message":"No record found!"}), 404# not found code


@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['DELETE'])
@auth.login_required
def delete_category(category_id):
    """function to delete recipe category of a user
    ---
    tags:
      - categories
    parameters:
      - in: path
        name: category_id
        description: Id of a category
        required: true
    responses:
      200:
        description: Ok
    """
    if category_id > 0:
        category = Category.query.filter_by(id=category_id).first()

        if not category:
            return jsonify({"Message":"No category with id {} was found!".format(category_id)}), 204# no content found
        else:
            category.delete()
            response = jsonify({"Message": "category {} was deleted successfully".format(category.name)}), 200#ok
            return response
    else:
        return jsonify({"Message":"Invalid category id {}".format(category_id)}), 404#bad request


@app.route('/recipe/api/v1.0/category/recipes', methods=['POST'])
@auth.login_required
def new_recipe():
    """function to create new recipe of a user
    ---
    tags:
      - recipes
    parameters:
      - in: body
        name: body
        description: a json object containing recipe details
        required: true
    responses:
      200:
        description: Ok
      201:
        description: New record created successfully
    """
    recipe_name = str(request.json.get('name', '')).strip()
    ingredients = str(request.json.get('ingredients', '')).strip()
    category_id = int(request.json.get('category_id', ''))


    if recipe_name and ingredients and category_id > 0:
        recipe = Recipe.query.filter_by(name=recipe_name).first()
        if not recipe:
            recipe = Recipe(category_id, recipe_name, ingredients)
            recipe.save()
            return jsonify({"message": "recipe {} was added successfully!".format(recipe.name)}), 201
        else:
            return jsonify({"message":"Recipe name already exits"}), 400
    else:
        return jsonify({"message":"Invalid values"}), 400


@app.route('/recipe/api/v1.0/category/recipes/<int:recipe_id>', methods=['PUT'])
@auth.login_required
def update_recipe(recipe_id):
    """function to update recipe of a user
    ---
    tags:
      - recipes
    parameters:
      - in: path
        name: recipe_id
        description: Id of a recipe
        required: true
      - in: body
        name: body
        description: a json object containing recipe details
        required: true
    responses:
      200:
        description: Ok
      201:
        description: New record created successfully
    """
    recipe_name = str(request.json.get('name', '')).strip()
    ingredients = str(request.json.get('ingredients', '')).strip()

    recipe = Recipe.query.filter_by(id=recipe_id).first()

    if not recipe:
        return jsonify({"Message":"No recipe with id {} was found!".format(recipe_id)}), 400

    if recipe_name and ingredients:
        recipe.name = recipe_name
        recipe.ingredients = ingredients
        recipe.date_modified = datetime.utcnow()
        recipe.save()
        return jsonify({"message": "recipe {} was updated successfully!".format(recipe.id)}), 201
    else:
        return jsonify({"message": "No recipes with id {} was found!".format(recipe_id)}), 204#



@app.route('/recipe/api/v1.0/category/recipes/', methods=['GET'])
@auth.login_required
def view_recipe():
    """function to view paginated recipes of a user
    ---
    tags:
      - recipes
    responses:
      200:
        description: Ok
    """
    pagination_helper = PaginationHelper(
        request,
        query=Recipe.query,
        resource_for_url='view_recipe',
        key_name='results',
        schema=recipe_schema)

    search = request.args.get('q')

    if search:
        pagination_helper = PaginationHelper(
            request,
            query=Recipe.query.filter(Recipe.name.contains(search)),
            resource_for_url='view_recipe',
            key_name='results',
            schema=recipe_schema)
        result = pagination_helper.paginate_query()
        if result['count']:
            return jsonify({'recipes':result}), 200
        else:
            return jsonify({"Message": 'No record matches search term'}), 204

    result = pagination_helper.paginate_query()
    if result['count']:
        return jsonify({'recipes':result}), 200
    print('not found')
    return jsonify({"Message":'No record found'}), 404


@app.route('/recipe/api/v1.0/category/recipes/<int:category_id>', methods=['GET'])
@auth.login_required
def view_recipe_by_category(category_id):
    """function to query all recipes in a particular category for a user
    ---
    tags:
      - recipes
    parameters:
      - in: path
        name: category_id
        description: Id of a category
        required: true
    responses:
      200:
        description: Ok
      204:
        description: No content found
      401:
        description: Unauthorized user
    """
    user = Users.query.filter_by(id=g.user.id).first()
    categorylists = Category.query.filter(Category.user_id == user.id, Category.id == category_id).first()
    recipes = Recipe.query.filter_by(category_id = category_id)

    if categorylists is None:
        response = jsonify({"Message": "No category with id {} was found!".format(category_id)}), 204#no content found
        return response

    if recipes is None:

        response = jsonify({"Message": "No recipes for category with id {} was found!".format(category_id)}), 204
        return response

    results = {}

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
                results["id"] = recipe.id
                results["name"] = recipe.name
                results["category"] = recipe.category_id
                results["ingredients"] = recipe.ingredients
                results["date_modified"] = recipe.date_modified

            response = jsonify(results), 200

            return response
    else:
        response = jsonify({"Message": "You don't have the right to view that recipe"}), 401#unauthorized user
        return response
    return jsonify({"Message":"No records found!"}), 204


@app.route('/recipe/api/v1.0/category/<int:category_id>/recipe/<int:recipe_id>', methods=['GET'])
@auth.login_required
def view_recipe_by_id(category_id, recipe_id):
    """function to query a particular recipe in a category for a user by id
    ---
    tags:
      - recipes
    parameters:
      - in: path
        name: category_id
        description: Id of a category
        required: true
      - in: path
        name: recipe_id
        description: Id of recipe
        required: true
    responses:
      200:
        description: Ok
      204:
        description: No content found
      401:
        description: Unauthorized user
    """

    user = Users.query.filter_by(id=g.user.id).first()
    categorylists = Category.query.filter(Category.user_id == user.id, Category.id == category_id).first()
    recipes = Recipe.query.filter(Recipe.id == recipe_id, Recipe.category_id == categorylists.id)


    if not categorylists:
        response = jsonify({"Message": "No category with id {} was found!".format(category_id)}), 204#no content found
        return response

    if not recipes:

        response = jsonify({"Message": "No recipe with id {} was found!".format(recipe_id)}), 204
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

            response = jsonify(results), 200


            return response
    else:
        response = jsonify({"Message": "You don't have the right to view that recipe"}), 401#unauthorized user
        return response
    return jsonify({"Message":"No records found!"}), 204


@app.route('/recipe/api/v1.0/category/recipes/<int:recipe_id>', methods=['DELETE'])
@auth.login_required
def delete_recipe(recipe_id):
    """function to delete a recipe from a category
    ---
    tags:
      - recipes
    parameters:
      - in: path
        name: recipe_id
        description: Id of a recipe
        required: true
    responses:
      200:
        description: Ok
      204:
        description: No content found
    """
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if not recipe:
        return jsonify({"Message":"No recipe with id {} was found!".format(recipe_id)}), 204#no content found
    else:
        recipe.delete()
        response = jsonify({"Message": "recipe {} deleted successfully!".format(recipe_id)}), 200
    return response

if __name__ == '__main__':
    app.run()

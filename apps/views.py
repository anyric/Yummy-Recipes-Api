"""view endpoint module that allow user to interact with the system"""
from datetime import datetime
from flask import request, jsonify, g
from apps import app, auth
from apps.user import Users
from apps.category import Category, CategorySchema
from apps.recipe import Recipe, RecipeSchema
from apps.paginate import PaginationHelper

category_schema = CategorySchema()
category_schema = CategorySchema(many=True)

recipe_schema = RecipeSchema()
recipe_schema = RecipeSchema(many=True)

@app.route('/recipe/api/v1.0/user/register', methods=['POST'])
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
      400:
        description: Bad Request
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
                return jsonify({"Message":"username {} already exits!".format(username)}), 400
            else:
                user = Users(firstname, lastname, username, password)
                user.save()
                response = jsonify({'Message': "user {} registered successfully!".format(user.username)}), 201
                return response
        else:
            return jsonify({"Message":"Only password can contain none alphabet character"}), 400

    return jsonify({"Message":"Please fill in all fields"}), 400



@app.route('/recipe/api/v1.0/user/update', methods=['PUT'])
@auth.login_required
def update_user_password():
    """function to update user password
    ---
    tags:
      - users
    parameters:
      - in: body
        name: body
        description: a dictionary containing old password and new password
        required: true
    responses:
      201:
        description: Password updated successfully!
      400:
        description: Bad Request
    """

    new_password = str(request.json.get('new_password', "")).strip()
    if new_password:

        if new_password.isalpha():
            return jsonify({"Message":"Password can't be only alphabets"}), 400

        if g.user.password == new_password:
            return jsonify({"Message":"New password can't be the same as old password"}), 400

        user_exit = Users.query.filter_by(username=g.user.username).first()
        if user_exit:
            user_exit.password = new_password
            user_exit.save()
            return jsonify({'Message':"Password updated successfully!"}), 201

    return jsonify({"Message":"Please provide new passwords"}), 400


@app.route('/recipe/api/v1.0/user/view', methods=['GET'])
@auth.login_required
def view_users():
    """function to view users list
    ---
    tags:
      - users
    responses:
      200:
        description: Ok
      204:
        description: No Content
    """
    userlist = Users.getusers()

    if userlist:
        return jsonify(userlist), 200
    else:
        return jsonify({"Message":"No registered user found!"}), 204


@auth.verify_password
def verify_password(username, password):
    """function to verify username and password"""
    user = Users.query.filter_by(username=username).first()

    if not user or not user.password == password:
        return False
    g.user = user
    return True

@app.route('/recipe/api/v1.0/user/delete', methods=['DELETE'])
@auth.login_required
def delete_user():
    """function to delete a user
    ---
    tags:
      - users
    responses:
      200:
        description: Ok
    """

    user = Users.query.filter_by(id=g.user.id).first()

    if user:
        user.delete()
        return jsonify({"Message": "user {} was deleted successfully".format(g.user.username)}), 200#ok


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
      201:
        description: New record created successfully
      400:
        description: Bad Request
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
      201:
        description: New record created successfully
      400:
        description: Bad Request
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
    function to view paginated recipe category of a user
    ---
    tags:
      - categories
    responses:
      200:
        description: Ok
      204:
        description: No Content
      404:
        description: Not Found
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

    return jsonify({"Message":"No record found"}), 404


@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['GET'])
@auth.login_required
def view_category_by_id(category_id):
    """function to view a recipe category of a user by category id
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
      204:
        description: No Content
      404:
        description: Not Found
    """
    if category_id > 0:
        user = Users.query.filter_by(id=g.user.id).first()
        categorylists = Category.query.filter(Category.id == category_id, Category.user_id == user.id).first()

        if not categorylists:
            return jsonify({"Message": "No category with id {} was found!".format(category_id)}), 204# no content found

        results = {}

        if user.id == categorylists.user_id:

            if categorylists:
                results["id"] = categorylists.id
                results["name"] = categorylists.name
                results["user"] = categorylists.user_id
                results["description"] = categorylists.description
                results["date_modified"] = categorylists.date_modified

                return jsonify(results), 200

    return jsonify({"Message":"No record found!"}), 404# not found code


@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['DELETE'])
@auth.login_required
def delete_category(category_id):
    """function to delete a recipe category of a user
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
      204:
        description: No Content
      404:
        description: Not Found
    """
    if category_id > 0:
        category = Category.query.filter_by(id=category_id).first()

        if not category:
            return jsonify({"Message":"No category with id {} was found!".format(category_id)}), 204# no content found
        else:
            category.delete()
            return jsonify({"Message": "category {} was deleted successfully".format(category.name)}), 200#ok
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
      201:
        description: New record created successfully
      400:
        description: Bad Request
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
      201:
        description: New record created successfully
      204:
        description: No Content
      400:
        description: Bad Request
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
        return jsonify({"message": "No recipes with id {} was found!".format(recipe_id)}), 204



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
      204:
        description: No Content
      404:
        description: Not Found
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
    else:
        result = pagination_helper.paginate_query()
        if result['count']:
            return jsonify({'recipes':result}), 200
        else:
            return jsonify({"Message":'No record found'}), 404


@app.route('/recipe/api/v1.0/category/recipes/<int:category_id>', methods=['GET'])
@auth.login_required
def view_recipe_by_category(category_id):
    """function to view all recipes in a particular category for a user
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
      400:
        description: Bad Request
    """
    user = Users.query.filter_by(id=g.user.id).first()

    if category_id > 0:
        categorylists = Category.query.filter(Category.user_id == user.id, Category.id == category_id).first()
        recipes = Recipe.query.filter_by(category_id=category_id)

        if not categorylists or not recipes:
            return jsonify({"Message": "No category with id {} was found!".format(category_id)}), 204#no content found

        results = {}
        for recipe in recipes:
            if recipe:
                results["id"] = recipe.id
                results["name"] = recipe.name
                results["category"] = recipe.category_id
                results["ingredients"] = recipe.ingredients
                results["date_modified"] = recipe.date_modified

                return jsonify(results), 200

    return jsonify({"Message":"Invalid category id!"}), 400


@app.route('/recipe/api/v1.0/category/<int:category_id>/recipes/<int:recipe_id>', methods=['GET'])
@auth.login_required
def view_recipe_by_id(category_id, recipe_id):
    """function to view a particular recipe in a category for a user by id
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
      400:
        description: Bad Request
    """

    user = Users.query.filter_by(id=g.user.id).first()

    if category_id > 0:
        categorylists = Category.query.filter(Category.user_id == user.id, Category.id == category_id).first()
        recipes = Recipe.query.filter(Recipe.id == categorylists.id, Recipe.id == recipe_id)

        results = {}
        for recipe in recipes:
            if recipe:
                results["id"] = recipe.id
                results["name"] = recipe.name
                results["category"] = recipe.category_id
                results["ingredients"] = recipe.ingredients
                results["date_modified"] = recipe.date_modified

                return jsonify(results), 200
    
    return jsonify({"Message":"Invalid category id!"}), 400

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
      400:
        description: Bad Request
    """
    if recipe_id > 0:
        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            return jsonify({"Message":"No recipe with id {} was found!".format(recipe_id)}), 204#no content found
        else:
            recipe.delete()
            return jsonify({"Message": "recipe {} deleted successfully!".format(recipe_id)}), 200

    return jsonify({"Message":"Invalid id"}), 400

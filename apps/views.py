"""view endpoint module that allow user to interact with the system"""
import datetime
from flask import request, jsonify, g, make_response, json
import jwt
from functools import wraps
from apps import app
from apps.user import Users, BlacklistTokens
from apps.category import Category, CategorySchema
from apps.recipe import Recipe, RecipeSchema
from apps.paginate import PaginationHelper

category_schema = CategorySchema()
category_schema = CategorySchema(many=True)

recipe_schema = RecipeSchema()
recipe_schema = RecipeSchema(many=True)

def token_required(function):
    """function to retrieve token from request header"""
    @wraps(function)
    def decorated(*args, **kwargs):
        """function to decode to token from the request header"""
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({"message":"Token is missing!"}), 401

        user_data = jwt.decode(token, app.config['SECRET'])
        if not user_data:
            return jsonify({"message":"Token is invalid!"}), 401

        if user_data:
            current_user = Users.query.filter_by(id=user_data['id']).first()

        return function(current_user, *args, **kwargs)

    return decorated


@app.route('/recipe/api/v1.0/user/register', methods=['POST'])
def register_new_user():
    """function to create new user
    ---
    tags:
      - users
    parameters:
      - in: body
        name: body
        description: a dictionary of user details
        required: true
        schema:
          id: register
          example: {"firstname":"Richard", "lastname":"Anyama",
          "username":"cooldev", "password":"cool1234"}
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
                return jsonify({"message":"Password can't be only alphabets"}), 400

            user_exit = Users.query.filter_by(username=username).first()
            if user_exit:
                return jsonify({"message":"username {} already exits!".format(username)}), 400
            else:
                user = Users(firstname, lastname, username, password)
                user.save()
                response = jsonify({'message': "user {} registered successfully!".\
                                    format(user.username)}), 201
                return response
        else:
            return jsonify({"message":"Only password can contain none alphabet character"}), 400

    return jsonify({"message":"Please fill in all fields"}), 400



@app.route('/recipe/api/v1.0/user/reset', methods=['PUT'])
@token_required
def update_user_password(current_user):
    """function to update user password
    ---
    tags:
      - users
    parameters:
      - in: body
        name: body
        description: a dictionary containing new password
        required: true
        schema:
          id: reset
          example: {"password":"dev1234"}
    responses:
      201:
        description: Password updated successfully!
      400:
        description: Bad Request
    """

    data = request.get_json()

    try:
        new_password = data['password']
    except KeyError:
        return jsonify({"message":"No password provided!"}), 400

    if new_password:

        if new_password.isalpha():

            return jsonify({"message":"Password can't be only alphabets"}), 400

        if current_user.password == new_password:
            return jsonify({"message":"New password can't be the same as old password"}), 400

        user_exit = Users.query.filter_by(username=current_user.username).first()
        if user_exit:
            user_exit.password = new_password
            user_exit.save()
            return jsonify({'message':"Password updated successfully!"}), 201


@app.route('/recipe/api/v1.0/user/view', methods=['GET'])
@token_required
def view_users(current_user):
    """function to view users list
    ---
    tags:
      - users
    responses:
      200:
        description: Ok
      404:
        description: Not Found
    """
    userlist = Users.getuser(current_user)

    if userlist:
        print(userlist)
        response = jsonify({"User":userlist}), 200
        # response = jsonify({"ammmmmm"})
    else:
        response = jsonify({"message":"No registered user found!"}), 404

    return response


@app.route('/recipe/api/v1.0/user/login', methods=['POST'])
def login_user():
    """function to login a user and get a token
    ---
    tags:
      - users
    parameters:
      - in: body
        name: body
        description: a dictionay of username and password for verification
        type: string
        required: true
        schema:
          id: login
          example: {"username":"cooldev", "password":"cool1234"}
    responses:
      200:
        description: Login successfully!
      401:
        description: Invalid username or password
    """
    username = str(request.json.get('username', '')).strip()
    password = str(request.json.get('password', '')).strip()

    if not username or not password:
        return make_response('Invalid username or password', 400, \
                                {'WWW-Authentication' : 'Basic realm="Login required!'})

    user = Users.query.filter(Users.username == username, Users.password == password).first()

    if user:
        token = BlacklistTokens.generate_token(user.id)
        return jsonify({'token': token.decode('UTF-8')}), 200


@app.route('/recipe/api/v1.0/user/logout')
@token_required
def logout(current_user):
    """function to logout users
    ---
    tags:
      - users
    responses:
      200:
        description: Ok
    """
    if not current_user:
        return jsonify({"message": "You are not login. Please log in!"}), 401

    token = request.headers['x-access-token']

    if token:
        blacklisted = BlacklistTokens.query.filter_by(token=token).first()
        if blacklisted:
            return jsonify({"message": "Token already blacklisted. Please login again!"}), 401

        blacklisttoken = BlacklistTokens(token=token)
        if blacklisttoken:
            blacklisttoken.save()
            return jsonify({"message": "Your loggout Successfully"}), 200

    else:
        return jsonify({"message": "Invalid token!"}), 401


@app.route('/recipe/api/v1.0/user/delete', methods=['DELETE'])
@token_required
def delete_user(current_user):
    """function to delete a user
    ---
    tags:
      - users
    responses:
      200:
        description: Ok
      401:
        description: Unauthorized user
    """
    if not current_user:
        return jsonify({"message":"You are not login, Please login first!"}), 401
    user = Users.query.filter_by(id=current_user.id).first()

    if user and user.id == current_user.id:
        user.delete()
        return jsonify({"message": "user {} was deleted successfully".\
                        format(current_user.username)}), 200#ok
    return jsonify({"message":"No user found!"}),

@app.route('/recipe/api/v1.0/category', methods=['POST'])
@token_required
def create_new_category(current_user):
    """function to create new recipe category of a user
    ---
    tags:
      - categories
    parameters:
      - in: body
        name: body
        description: a dictionary containing details of a category to be added
        required: true
        schema:
          id: category
          example: {"name":"black tea", "description":"a list of recipe categories"}
    responses:
      201:
        description: New record created successfully
      400:
        description: Bad Request
    """

    data = request.get_json()

    category_name = data['name']
    description = data['description']

    if category_name and description:
        cat_exits = Category.query.filter(Category.name == category_name, \
        Category.user_id == current_user.id).first()

        if cat_exits:
            return jsonify({"message":"Category {} already exits".format(category_name)}), 400
        else:
            category = Category(current_user.id, category_name, description)
            category.save()

            return jsonify({"message":"category {} was added successfully!".\
                            format(category.name)}), 201
    else:
        return jsonify({"message":"Please enter all details!"}), 400


@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['PUT'])
@token_required
def update_category(current_user, category_id):
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
        description: a dictionary containing details of a category to be updated
        required: true
        schema:
          id: update_category
          example: {"name":"black tea", "description":"a list of recipe categories"}
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
        return jsonify({"message":"No category found!"}), 400

    if category_name and description and category.user_id == current_user.id:

        category.name = category_name
        category.description = description
        category.date_modified = datetime.datetime.utcnow()
        category.save()
        return jsonify({"message": "category {} was updated successfully".format(category.id)}), 201
    else:
        return jsonify({"message": "Please enter new details and \
                        ensure the category is yours!"}), 400


@app.route('/recipe/api/v1.0/category/', methods=['GET'])
@token_required
def view_category(current_user):
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
    pagination_helper = PaginationHelper(
        request,
        query=Category.query.filter(Category.user_id == current_user.id),
        resource_for_url='view_category',
        key_name='results',
        schema=category_schema)

    search = request.args.get('q')


    if search:

        pagination_helper = PaginationHelper(
            request,
            query=Category.query.filter(Category.user_id == current_user.id, \
                                        Category.name.contains(search)),
            resource_for_url='view_category',
            key_name='results',
            schema=category_schema)

        result = pagination_helper.paginate_query()
        if result['count']:
            return jsonify({'categories':result}), 200
        else:
            return jsonify({'Message':"No record matches search term"}), 404

    result = pagination_helper.paginate_query()
    if result['count'] > 0:
        return jsonify({'categories':result}), 200

    return jsonify({"message":"No record found"}), 404


@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['GET'])
@token_required
def view_category_by_id(current_user, category_id):
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

        categorylists = Category.query.filter(Category.id == category_id, \
                                                Category.user_id == current_user.id).first()

        if not categorylists:
            return jsonify({"message": "No category found!"}), 404

        results = {}

        if current_user.id == categorylists.user_id:

            if categorylists:
                results["id"] = categorylists.id
                results["name"] = categorylists.name
                results["user"] = categorylists.user_id
                results["description"] = categorylists.description
                results["date_modified"] = categorylists.date_modified

                return jsonify(results), 200

    return jsonify({"message":"No record found!"}), 404# not found code


@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['DELETE'])
@token_required
def delete_category(current_user, category_id):
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
        category = Category.query.filter(Category.id == category_id, \
                                        Category.user_id == current_user.id).first()

        if not category:
            return jsonify({"message":"No category found!"}), 404
        else:
            category.delete()
            return jsonify({"message": "category {} was deleted successfully".\
                            format(category.name)}), 200
    else:
        return jsonify({"message":"Invalid category id"}), 404


@app.route('/recipe/api/v1.0/category/recipes', methods=['POST'])
@token_required
def new_recipe(current_user):
    """function to create new recipe of a user
    ---
    tags:
      - recipes
    parameters:
      - in: body
        name: body
        description: a dictionary containing details of a recipe to be added
        required: true
        schema:
          id: recipe
          example: {"name":"black tea", "ingredients":"tea leave, sugar,
          hot water", "category_id":1}
    responses:
      201:
        description: New record created successfully
      400:
        description: Bad Request
    """
    recipe_name = str(request.json.get('name', '')).strip()
    ingredients = str(request.json.get('ingredients', '')).strip()
    category_id = int(request.json.get('category_id', ''))

    category = Category.query.filter(Category.id == category_id, \
                                    Category.user_id == current_user.id)

    if not category:
        return jsonify({"message":"No category found!"}), 404

    if recipe_name and ingredients and category_id > 0:
        recipe = Recipe.query.filter_by(name=recipe_name).first()
        if not recipe:
            recipe = Recipe(category_id, recipe_name, ingredients)
            recipe.save()
            return jsonify({"message": "recipe {} was added successfully!".\
                            format(recipe.name)}), 201
        else:
            return jsonify({"message":"Recipe name already exits"}), 400
    else:
        return jsonify({"message":"Invalid values"}), 400


@app.route('/recipe/api/v1.0/category/recipes/<int:recipe_id>', methods=['PUT'])
@token_required
def update_recipe(current_user, recipe_id):
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
        description: a dictionary containing details of a recipe to be updated
        required: true
        schema:
          id: update_recipe
          example: {"name":"black tea", "ingredients":"tea leave, sugar,
          hot water", "category_id":1}
    responses:
      201:
        description: Record updated successfully
      204:
        description: No Content
      400:
        description: Bad Request
    """
    category = Category.query.filter_by(user_id=current_user.id)

    if not category:
        return jsonify({"message":"Recipe {} doesn't blong to you!".\
                        format(recipe_id)}), 400

    recipe_name = str(request.json.get('name', '')).strip()
    ingredients = str(request.json.get('ingredients', '')).strip()

    recipe = Recipe.query.filter_by(id=recipe_id).first()

    if not recipe:
        return jsonify({"message":"No recipe with id {} was found or doesn't blongs to you!"}), 404

    if recipe_name and ingredients:
        recipe.name = recipe_name
        recipe.ingredients = ingredients
        recipe.date_modified = datetime.datetime.utcnow()
        recipe.save()
        return jsonify({"message": "recipe {} was updated successfully!".format(recipe.id)}), 201
    else:
        return jsonify({"message": "No recipes with id {} was found!".format(recipe_id)}), 404


@app.route('/recipe/api/v1.0/category/recipes/', methods=['GET'])
@token_required
def view_recipe(current_user):
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

    category = Category.query.filter_by(user_id=current_user.id)

    if not category:
        return jsonify({"message":"Recipe doesn't blong to you!"}), 401

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
            return jsonify({"message": 'No record found'}), 404
    else:
        result = pagination_helper.paginate_query()
        if result['count'] > 0:
            return jsonify({'recipes':result}), 200
        else:
            return jsonify({"message":'No record found'}), 404


@app.route('/recipe/api/v1.0/category/recipes/<int:category_id>', methods=['GET'])
@token_required
def view_recipe_by_category(current_user, category_id):
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

    if category_id > 0:
        categorylists = Category.query.filter(Category.user_id == current_user.id, \
                                                Category.id == category_id).first()
        recipes = Recipe.query.filter_by(category_id=category_id)

        if not categorylists or not recipes or not categorylists.user_id == current_user.id:
            return jsonify({"message": "No record found!"}), 404

        results = {}
        for recipe in recipes:
            if recipe:
                results["id"] = recipe.id
                results["name"] = recipe.name
                results["category"] = recipe.category_id
                results["ingredients"] = recipe.ingredients
                results["date_modified"] = recipe.date_modified

                return jsonify(results), 200

    return jsonify({"message":"Invalid category id!"}), 400


@app.route('/recipe/api/v1.0/category/<int:category_id>/recipes/<int:recipe_id>', methods=['GET'])
@token_required
def view_recipe_by_id(current_user, category_id, recipe_id):
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

    if category_id > 0 and recipe_id > 0:
        categorylists = Category.query.filter(Category.user_id == current_user.id, \
                                                Category.id == category_id).first()
        recipes = Recipe.query.filter(Recipe.id == categorylists.id, Recipe.id == recipe_id)

        if not categorylists or not recipes:
            return jsonify({"message": "No record found!"}), 404

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
@token_required
def delete_recipe(current_user, recipe_id):
    """function to delete a recipe from a category
    ---
    tags:
      - recipes
    parameters:
      - in: path
        name: recipe_id
        description: Id of a recipe
        required: true
    security:
      - TokenHeader: []
    responses:
      200:
        description: Ok
      204:
        description: No content found
      400:
        description: Bad Request
    """
    category = Category.query.filter_by(user_id=current_user.id)

    if not category:
        return jsonify({"message":"Recipe doesn't blong to you!"}), 401

    if recipe_id > 0:
        recipe = Recipe.query.filter_by(id=recipe_id).first()

        if not recipe:
            return jsonify({"message":"No recipe found!"}), 404
        else:
            recipe.delete()
            return jsonify({"message": "recipe {} deleted successfully!".format(recipe_id)}), 200

    return jsonify({"message":"Invalid id"}), 400

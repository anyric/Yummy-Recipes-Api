"""module for recipe model view """
import datetime
from flask import request, jsonify

from apps.models.category import Category
from apps.models.recipe import Recipe, RecipeSchema
from apps.utilities.decode_token import token_required

from apps import app
from apps.utilities.paginate import PaginationHelper

recipe_schema = RecipeSchema()
recipe_schema = RecipeSchema(many=True)


@app.errorhandler(404)
def pageNotFound(error):
    """function to handle internal server errors"""
    return jsonify({"message":"page not found!"}), 404

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
    data = request.get_json()
    recipe_name = str(data['name']).strip()
    ingredients = str(data['ingredients']).strip()
    category_id = data['category_id']

    if recipe_name and ingredients and category_id and isinstance(category_id, int) and category_id > 0:
        category = Category.query.filter(Category.id == category_id, \
                                        Category.user_id == current_user.id).first()

        if not category:
            return jsonify({"message":"wrong category id or don't belong to you!"}), 404

        recipe = Recipe.query.filter_by(name=recipe_name).first()
        if not recipe:
            recipe = Recipe(category_id, current_user.id, recipe_name, ingredients)
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
        description: Id of a recipe e.g 2
        required: true
      - in: body
        name: body
        description: a dictionary containing details of a recipe to be updated
        required: true
        schema:
          id: update_recipe
          example: {"name":"black tea", "ingredients":"tea leave, sugar, hot water"}
    responses:
      201:
        description: Record updated successfully
      400:
        description: Bad Request
    """
    recipe_name = str(request.json.get('name', '')).strip()
    ingredients = str(request.json.get('ingredients', '')).strip()

    recipe = Recipe.query.filter(Recipe.id == recipe_id, Recipe.user_id == current_user.id).first()

    if not recipe:
        return jsonify({"message":"No recipe with id {} was found or doesn't blongs to you!".\
                        format(recipe_id)}), 404

    if recipe_name and ingredients and not recipe.name == recipe_name:
        recipe.name = recipe_name
        recipe.ingredients = ingredients
        recipe.date_modified = datetime.datetime.utcnow()
        recipe.save()
        return jsonify({"message": "recipe {} was updated successfully!".format(recipe.id)}), 201
    else:
        return jsonify({"message": " recipes with name {} already exists!".\
                        format(recipe_name)}), 404


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
      404:
        description: Not Found
    """
    pagination_helper = PaginationHelper(
        request,
        query=Recipe.query,
        resource_for_url='view_recipe',
        key_name='results',
        schema=recipe_schema)

    search = request.args.get('q', type=str)
    page = request.args.get('page', default=1, type=int)

    if not search is None:
        pagination_helper = PaginationHelper(
            request,
            query=Recipe.query.filter(Recipe.name.contains(search), \
            Recipe.user_id == current_user.id),
            resource_for_url='view_recipe',
            key_name='results',
            schema=recipe_schema)
        result = pagination_helper.paginate_query()
        if page and isinstance(page, int):
            if page > result['pages'] or page <= 0 or isinstance(page, str):
                return jsonify({"message":"invalid search or page doesn't exist!"}), 404

        if result['items'] > 0:
            response = jsonify({'recipe':result}), 200
        else:
            response = jsonify({"message": 'No record found'}), 404
    else:
        result = pagination_helper.paginate_query()
        if page and isinstance(page, int):
            if page > result['pages'] or page <= 0 or isinstance(page, str):
                return jsonify({"message":"page doesn't exist!"}), 404

        if result['items'] > 0:
            response = jsonify({'recipe':result}), 200
        else:
            response = jsonify({"message":'No record found'}), 404
    return response

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

    if isinstance(category_id, int) and category_id > 0:
        recipes = Recipe.query.filter(Recipe.category_id == category_id, \
        Recipe.user_id == current_user.id).all()

        if not recipes:
            return jsonify({"message":'No recipe found'}), 404

        results = []
        for recipe in recipes:
            obj = {
                "id": recipe.id,
                "name": recipe.name,
                "ingredients": recipe.ingredients,
                "category_id": recipe.category_id,
                "date_modified": recipe.date_modified
            }
            results.append(obj)
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
    if isinstance(recipe_id, int) and isinstance(category_id, int) and category_id > 0 and recipe_id > 0:
        recipes = Recipe.query.filter(Recipe.category_id == category_id, Recipe.id == recipe_id, \
        Recipe.user_id == current_user.id)

        if not recipes:
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

    return jsonify({"Message":"Invalid category or recipe id!"}), 400

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
    if isinstance(recipe_id, int) and recipe_id > 0:
        recipe = Recipe.query.filter(Recipe.id == recipe_id, \
        Recipe.user_id == current_user.id).first()

        if not recipe:
            return jsonify({"message":"No recipe found!"}), 404
        else:
            recipe.delete()
            return jsonify({"message": "recipe {} deleted successfully!".format(recipe_id)}), 200

    return jsonify({"message":"Invalid id"}), 400

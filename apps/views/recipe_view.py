"""module for recipe model view """
import datetime
from flask import request, jsonify
from flasgger import swag_from

from apps.models.category import Category
from apps.models.recipe import Recipe, RecipeSchema
from apps.utilities.decode_token import token_required

from apps import app
from apps.utilities.paginate import PaginationHelper

recipe_schema = RecipeSchema()
recipe_schema = RecipeSchema(many=True)

def display(page, result):
    "function to display recipe"
    if page and isinstance(page, int):
        if page > result['pages'] or page <= 0 or isinstance(page, str):
            response = jsonify({"message":"invalid search or page doesn't exist!"}), 404
        else:
            if result['items'] > 0:
                response = jsonify({'recipe':result}), 200
            else:
                response = jsonify({"message": 'No record found'}), 404
    else:
        response = jsonify({"message":"invalid page number!"}), 404
    return response

@app.route('/recipe/api/v1.0/category/recipes', methods=['POST'])
@token_required
@swag_from("/apps/docs/newrecipe.yml")
def new_recipe(current_user):
    """function to create new recipe of a user"""
    data = request.get_json()
    recipe_name = str(data['name']).strip()
    ingredients = str(data['ingredients']).strip()
    category_id = data['category_id']
    if recipe_name and ingredients and category_id and isinstance(category_id, int) \
        and category_id > 0:
        category = Category.get_category_by_id(category_id, current_user)
        if not category:
            response = jsonify({"message":"wrong category id or don't belong to you!"}), 404
        else:
            recipe = Recipe.query.filter_by(name=recipe_name.lower()).first()
            if not recipe:
                recipe = Recipe(category_id, current_user.id, recipe_name.lower(), ingredients)
                recipe.save()
                response = jsonify({"message": "recipe {} was added successfully!".\
                                format(recipe.name)}), 201
            else:
                response = jsonify({"message":"Recipe name {} already exits".\
                                    format(recipe_name)}), 400
    else:
        response = jsonify({"message":"Invalid values"}), 400
    return response

@app.route('/recipe/api/v1.0/category/recipes/<int:recipe_id>', methods=['PUT'])
@token_required
@swag_from("/apps/docs/updaterecipe.yml")
def update_recipe(current_user, recipe_id):
    """function to update recipe of a user"""
    recipe_name = str(request.json.get('name', '')).strip()
    ingredients = str(request.json.get('ingredients', '')).strip()
    recipe = Recipe.get_recipe_by_id(recipe_id, current_user)
    if not recipe:
        response = jsonify({"message":"No recipe with id {} was found or doesn't blongs to you!".\
                        format(recipe_id)}), 404
    else:
        if recipe_name and ingredients and not recipe.name == recipe_name:
            recipe.update_recipe(recipe_name.lower(), ingredients)
            response = jsonify({"message": "recipe {} was updated successfully!".\
            format(recipe.id)}), 201
        else:
            response = jsonify({"message": " recipes with name {} already exists!".\
                            format(recipe_name)}), 404
    return response

@app.route('/recipe/api/v1.0/category/recipes/', methods=['GET'])
@token_required
@swag_from("/apps/docs/viewrecipe.yml")
def view_recipe(current_user):
    """function to view paginated recipes of a user"""
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
            query=Recipe.query.filter(Recipe.name.contains(search.lower()), \
            Recipe.user_id == current_user.id),
            resource_for_url='view_recipe',
            key_name='results',
            schema=recipe_schema)
        result = pagination_helper.paginate_query()
        response = display(page, result)
    else:
        result = pagination_helper.paginate_query()
        response = display(page, result)
    return response

@app.route('/recipe/api/v1.0/category/recipes/<int:category_id>', methods=['GET'])
@token_required
@swag_from("/apps/docs/viewrecipebycatid.yml")
def view_recipe_by_category(current_user, category_id):
    """function to view all recipes in a particular category for a user"""
    if isinstance(category_id, int) and category_id > 0:
        recipes = Recipe.get_recipe_category_id(category_id, current_user)
        if not recipes:
            response = jsonify({"message":'No recipe found'}), 404
        else:
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
            response = jsonify(results), 200
    else:
        response = jsonify({"message":"Invalid category id!"}), 400
    return response

@app.route('/recipe/api/v1.0/category/<int:category_id>/recipes/<int:recipe_id>', methods=['GET'])
@token_required
@swag_from("/apps/docs/viewrecipebycatrecid.yml")
def view_recipe_by_id(current_user, category_id, recipe_id):
    """function to view a particular recipe in a category for a user by id"""
    if isinstance(recipe_id, int) and isinstance(category_id, int) and \
        category_id > 0 and recipe_id > 0:
        recipe = Recipe.get_by_recipe_category_id(category_id, recipe_id, current_user)
        if not recipe:
            response = jsonify({"message": "No record found!"}), 404
        else:
            results = {}
            results["id"] = recipe.id
            results["name"] = recipe.name
            results["category"] = recipe.category_id
            results["ingredients"] = recipe.ingredients
            results["date_modified"] = recipe.date_modified
            response = jsonify(results), 200
    else:
        response = jsonify({"Message":"Invalid category or recipe id!"}), 400
    return response

@app.route('/recipe/api/v1.0/category/recipes/<int:recipe_id>', methods=['DELETE'])
@token_required
@swag_from("/apps/docs/deleterecipe.yml")
def delete_recipe(current_user, recipe_id):
    """function to delete a recipe from a category"""
    if isinstance(recipe_id, int) and recipe_id > 0:
        recipe = Recipe.get_recipe_by_id(recipe_id, current_user)
        if not recipe:
            response = jsonify({"message":"No recipe found!"}), 404
        else:
            recipe.delete()
            response = jsonify({"message": "recipe {} deleted successfully!".\
                                format(recipe_id)}), 200
    else:
        response = jsonify({"message":"Invalid id"}), 400
    return response

"""module for category view """
import datetime
from flask import request, jsonify
from flasgger import swag_from

from apps.models.category import Category, CategorySchema
from apps.utilities.decode_token import token_required
from apps import app
from apps.utilities.paginate import PaginationHelper

category_schema = CategorySchema()
category_schema = CategorySchema(many=True)

def display(page, result):
    """function to view category"""
    if page and isinstance(page, int):
        if page > result['pages'] or page <= 0 or isinstance(page, str):
            response = jsonify({"message":"invalid search or page doesn't exist!"}), 404
        else:
            if result['items'] > 0:
                response = jsonify({'category':result}), 200
            else:
                response = jsonify({"message": 'No record found'}), 404
    else:
        response = jsonify({"message":"invalid page number!"}), 404
    return response

@app.route('/recipe/api/v1.0/category', methods=['POST'])
@token_required
@swag_from("/apps/docs/newcategory.yml")
def create_new_category(current_user):
    """function to create new recipe category of a user"""
    data = request.get_json()
    category_name = data['name']
    description = data['description']
    if category_name and description and isinstance(category_name, str) and \
        isinstance(description, str):
        cat_exits = Category.get_category_by_name(category_name, current_user)
        if cat_exits:
            response = jsonify({"message":"Category {} already exits".format(category_name)}), 400
        else:
            category = Category(current_user.id, category_name.lower(), description)
            category.save()
            response = jsonify({"message":"category {} was added successfully!".\
                            format(category.name)}), 201
    else:
        response = jsonify({"message":"Please enter all details!"}), 400
    return response

@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['PUT'])
@token_required
@swag_from("/apps/docs/updatecategory.yml")
def update_category(current_user, category_id):
    """function to update category for a user"""
    data = request.get_json()
    category_name = str(data['name']).strip()
    description = str(data['description']).strip()
    category = Category.get_category_by_id(category_id, current_user)
    if not category:
        response = jsonify({"message":"No category found!"}), 400
    else:
        if category_name and description and category.user_id == current_user.id:
            category.update(category_name.lower(), description)
            response = jsonify({"message": "category {} was updated successfully".\
                                format(category.id)}), 201
        else:
            response = jsonify({"message": "Please enter new details and \
                        ensure the category is yours!"}), 400
    return response

@app.route('/recipe/api/v1.0/category/', methods=['GET'])
@token_required
@swag_from("/apps/docs/viewcategory.yml")
def view_category(current_user):
    """function to view paginated recipe category of a user"""
    pagination_helper = PaginationHelper(
        request,
        query=Category.query.filter(Category.user_id == current_user.id),
        resource_for_url='view_category',
        key_name='results',
        schema=category_schema)
    search = request.args.get('q', type=str)
    page = request.args.get('page', default=1, type=int)
    if not search is None:
        pagination_helper = PaginationHelper(
            request,
            query=Category.query.filter(Category.user_id == current_user.id, \
            Category.name.contains(search.lower())),
            resource_for_url='view_category',
            key_name='results',
            schema=category_schema)
        result = pagination_helper.paginate_query()
        response = display(page, result)
    else:
        result = pagination_helper.paginate_query()
        response = display(page, result)
    return response

@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['GET'])
@token_required
@swag_from("/apps/docs/viewcategorybyid.yml")
def view_category_by_id(current_user, category_id):
    """function to view a recipe category of a user by category id"""
    if isinstance(category_id, int) and category_id > 0 and current_user:
        categorylists = Category.get_category_by_id(category_id, current_user)

        if not categorylists:
            response = jsonify({"message": "No category found!"}), 404
        else:
            results = {}
            results["id"] = categorylists.id
            results["name"] = categorylists.name
            results["user"] = categorylists.user_id
            results["description"] = categorylists.description
            results["date_modified"] = categorylists.date_modified
            response = jsonify(results), 200
    else:
        return jsonify({"message":"invalid value!"}), 404
    return response

@app.route('/recipe/api/v1.0/category/<int:category_id>', methods=['DELETE'])
@token_required
@swag_from("/apps/docs/deletecategory.yml")
def delete_category(current_user, category_id):
    """function to delete a recipe category of a user"""
    if isinstance(category_id, int) and category_id > 0 and current_user:
        category = Category.get_category_by_id(category_id, current_user)

        if not category:
            response = jsonify({"message":"No category found!"}), 404
        else:
            category.delete()
            response = jsonify({"message": "category {} was deleted successfully".\
                            format(category.name)}), 200
    else:
        response = jsonify({"message":"Invalid category id"}), 404
    return response

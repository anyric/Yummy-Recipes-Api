"""module for category view """
import datetime
from flask import request, jsonify

from apps.models.category import Category, CategorySchema
from apps.utilities.decode_token import token_required
from apps import app
from apps.utilities.paginate import PaginationHelper

category_schema = CategorySchema()
category_schema = CategorySchema(many=True)

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
          example: {"name":"break", "description":"a list of food for break fast"}
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
        description: Id of a category e.g 1
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
    data = request.get_json()
    category_name = str(data['name']).strip()
    description = str(data['description']).strip()
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

    search = request.args.get('q', type=str)
    page = request.args.get('page', default=1, type=int)

    if not search is None:

        pagination_helper = PaginationHelper(
            request,
            query=Category.query.filter(Category.user_id == current_user.id, \
            Category.name.contains(search)),
            resource_for_url='view_category',
            key_name='results',
            schema=category_schema)

        result = pagination_helper.paginate_query()
        if page and isinstance(page, int):
            if page > result['pages'] or page <= 0 or isinstance(page, str):
                return jsonify({"message":"invalid search or page doesn't exist!"}), 404

        if result['items'] > 0:
            response = jsonify({'category':result}), 200
        else:
            response = jsonify({'Message':"No record matches search term!"}), 404
    else:
        result = pagination_helper.paginate_query()
        if page and isinstance(page, int):
            if page > result['pages'] or page <= 0 or isinstance(page, str):
                return jsonify({"message":"page doesn't exist!"}), 404

        if result['items'] > 0:
            response = jsonify({'category':result}), 200
        else:
            response = jsonify({'Message':"No record found!"}), 404
    return response

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
        description: Id of a category e.g 2
        required: true
    responses:
      200:
        description: Ok
      404:
        description: Not Found
    """
    if isinstance(category_id, int) and category_id > 0 and current_user:
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
    else:
        return jsonify({"message":"invalid value!"}), 404


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
      404:
        description: Not Found
    """
    if isinstance(category_id, int) and category_id > 0 and current_user:
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

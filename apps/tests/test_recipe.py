"""module to test recipe view"""
from flask_testing import TestCase
import json

from apps import app, db
from apps import config
from apps.models.category import Category
from apps.models.recipe import Recipe
from apps.models.user import Users

class RecipeTests(TestCase):
    """class to test user views"""
    def create_app(self):
        return app

    def setUp(self):
        """function to setup app variables"""
        config_name = config.TestingConfig
        app.config.from_object(config_name)
        self.app = app
        self.test_client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.name = 'test user'
        self.email = 'testuser@example.com'
        self.test_username = 'testuser'
        self.test_password = 'test1234'
        with self.app_context:
            db.create_all()

    def tearDown(self):
        """function to delete test_db after every test case"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_header_token(self):
        """function to retrieve token from header"""
        data = {"username":self.test_username, "password":self.test_password}
        response = self.test_client.post('/recipe/api/v1.0/user/login', data=json.dumps(data), \
                                            content_type='application/json')
        res = json.loads(response.data.decode())['token']
        token = {"x-access-token": res}
        return token

    def register_new_user(self, name, email, username, password):
        """function to register_new_user view"""
        data = {'name': name, 'email':email, \
                'username':username, 'password': password}
        response = self.client.post('/recipe/api/v1.0/user/register', data=json.dumps(data), \
                                    content_type='application/json')
        return response

    def create_new_category(self, user_id, name, description):
        """function to create_new_category view"""
        data = {'user_id':user_id, 'name':name, 'description':description}
        response = self.test_client.post('/recipe/api/v1.0/category', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        return response

    def create_new_recipe(self, category_id, user_id, name, ingredients):
        """helper function to create_new_recipe """
        data = {'category_id':category_id, 'user_id':user_id, \
        'name':name, 'ingredients':ingredients}
        response = self.test_client.post('/recipe/api/v1.0/category/recipes', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        return response

    def test_create_new_recipe(self):
        """function to test create_new_recipe """
        #registering recipe user
        self.register_new_user(self.name, self.email, \
        self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        response = self.create_new_recipe(category.id, user.id, name, ingredients)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Recipe.query.count(), 1)

    def test_new_recipe_missing_value(self):
        """function to test create_new_recipe missing value"""
        #registering recipe user
        self.register_new_user(self.name, self.email, \
        self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        ingredients = 'Tea leave, sugar, hot water'
        data = {'category_id':category.id, 'user_id':user.id, 'name':'', 'ingredients':ingredients}
        response = self.test_client.post('/recipe/api/v1.0/category/recipes', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_new_recipe_wrong_category_id(self):
        """function to test create_new_recipe missing value"""
        #registering recipe user
        self.register_new_user(self.name, self.email, \
        self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        # category = Category.query.filter_by(name=category_name).first()
        name = 'black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        data = {'category_id':2, 'user_id':user.id, 'name':name, \
                'ingredients':ingredients}
        response = self.test_client.post('/recipe/api/v1.0/category/recipes', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_new_recipe_already_exists(self):
        """function to test create_new_recipe name already exists """
        #registering recipe user
        self.register_new_user(self.name, self.email, \
        self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        self.create_new_recipe(category.id, user.id, name, ingredients)
        data = {'category_id':category.id, 'user_id':user.id, \
                'name':name, 'ingredients':ingredients}
        response = self.test_client.post('/recipe/api/v1.0/category/recipes', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_missing_recipe(self):
        """function to test update_recipe missing recipe """
        #registering recipe user
        self.register_new_user(self.name, self.email, \
        self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        self.create_new_recipe(category.id, user.id, name, ingredients)
        data = {'category_id':category.id, 'ingredients':ingredients}
        response = self.test_client.put('/recipe/api/v1.0/category/recipes/2', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_update_missing_value(self):
        """function to test update_recipe missing value """
        #registering recipe user
        self.register_new_user(self.name, self.email, \
        self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        self.create_new_recipe(category.id, user.id, name, ingredients)
        data = {'category_id':category.id, 'ingredients':ingredients}
        response = self.test_client.put('/recipe/api/v1.0/category/recipes/1', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_update_recipe(self):
        """function to test update_recipe value """
        #registering recipe user
        self.register_new_user(self.name, self.email, \
        self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        self.create_new_recipe(category.id, user.id, name, ingredients)
        data = {'name':'coffee', 'ingredients':'coffee, sugar, hot water'}
        response = self.test_client.put('/recipe/api/v1.0/category/recipes/1', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_view_recipe(self):
        """function to test view_recipe endpoint """
        #registering recipe user
        self.register_new_user(self.name, self.email, self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        self.create_new_recipe(category.id, user.id, name, ingredients)
        response = self.test_client.get('/recipe/api/v1.0/category/recipes/', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_view_recipe_search_ok(self):
        """function to test view_recipe with valid search term """
        #registering recipe user
        self.register_new_user(self.name, self.email, \
        self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        self.create_new_recipe(category.id, user.id, name, ingredients)
        response = self.test_client.get('/recipe/api/v1.0/category/recipes/?q=b', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_view_recipe_search_invalid(self):
        """function to test view_recipe with invalid search term """
        #registering recipe user
        self.register_new_user(self.name, self.email, \
        self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        self.create_new_recipe(category.id, user.id, name, ingredients)
        response = self.test_client.get('/recipe/api/v1.0/category/recipes/?q=b', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_view_recipe_not_found(self):
        """function to test view_recipe endpoint not found"""
        #registering recipe user
        self.register_new_user(self.name, self.email, self.test_username, self.test_password)
        response = self.test_client.get('/recipe/api/v1.0/category/recipes/', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_view_recipe_bad_request(self):
        """function to test view_recipe endpoint with bad request"""
        #registering recipe user
        self.register_new_user(self.name, self.email, self.test_username, \
        self.test_password)
        response = self.test_client.get('/recipe/api/v1.0/category/recipes/0', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_view_recipe_unauthorized(self):
        """function to test view_recipe by category id endpoint unauthorized"""
        #registering recipe user
        self.register_new_user(self.name, self.email, self.test_username, \
        self.test_password)
        self.register_new_user('test', 'test@example.com', 'test', 'j1234')
        user = Users.query.filter_by(username='test').first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        self.create_new_recipe(category.id, user.id, name, ingredients)
        response = self.test_client.get('/recipe/api/v1.0/category/recipes/1')
        self.assertEqual(response.status_code, 401)

    def test_view_recipe_no_content(self):
        """function to test view_recipe by category id endpoint no content found"""
        #registering recipe user
        self.register_new_user(self.name, self.email, self.test_username, \
        self.test_password)
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(2, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        user = Users.query.filter_by(username=self.test_username).first()
        self.create_new_recipe(category.id, user.id, name, ingredients)
        response = self.test_client.get('/recipe/api/v1.0/category/recipes/2', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_view_recipe_by_category_ok(self):
        """function to test view_recipe by category id"""
        #registering recipe user
        self.register_new_user(self.name, self.email, self.test_username, \
        self.test_password)
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(2, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        user = Users.query.filter_by(username=self.test_username).first()
        self.create_new_recipe(category.id, user.id, name, ingredients)
        response = self.test_client.get('/recipe/api/v1.0/category/recipes/1', headers=\
       self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_view_recipe_by_category_recipe_ok(self):
        """function to test view_recipe by category id"""
        #registering recipe user
        self.register_new_user(self.name, self.email, self.test_username, \
        self.test_password)
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(2, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        user = Users.query.filter_by(username=self.test_username).first()
        user = Users.query.filter_by(username=self.test_username).first()
        self.create_new_recipe(category.id, user.id, name, ingredients)
        response = self.test_client.get('/recipe/api/v1.0/category/1/recipes/1', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_view_recipe_category_no_recipe(self):
        """function to test view_recipe with wrong recipe id"""
        #registering recipe user
        self.register_new_user(self.name, self.email, self.test_username, \
        self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        user = Users.query.filter_by(username=self.test_username).first()
        self.create_new_recipe(category.id, user.id, name, ingredients)
        response = self.test_client.get('/recipe/api/v1.0/category/1/recipes/2', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_recipe_by_id_bad_request(self):
        """function to test view_recipe with no category and recipe found"""
        #registering recipe user
        self.register_new_user(self.name, self.email, self.test_username, \
        self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        user = Users.query.filter_by(username=self.test_username).first()
        self.create_new_recipe(category.id, user.id, name, ingredients)
        response = self.test_client.delete('/recipe/api/v1.0/category/recipes/0', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_delete_recipe_no_content(self):
        """function to test view_recipe with no category and recipe found"""
        #registering recipe user
        self.register_new_user(self.name, self.email, self.test_username, \
        self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        user = Users.query.filter_by(username=self.test_username).first()
        self.create_new_recipe(category.id, user.id, name, ingredients)
        response = self.test_client.delete('/recipe/api/v1.0/category/recipes/3', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_recipe_by_id_ok(self):
        """function to test view_recipe with no category and recipe found"""
        #registering recipe user
        self.register_new_user(self.name, self.email, self.test_username, \
        self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        user = Users.query.filter_by(username=self.test_username).first()
        self.create_new_recipe(category.id, user.id, name, ingredients)
        response = self.test_client.delete('/recipe/api/v1.0/category/recipes/1', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 200)

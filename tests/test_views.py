""" module to test views.py"""
from flask_testing import TestCase
import json
from werkzeug.datastructures import Headers
from apps import app, db
from apps import config
from apps.user import Users
from apps.category import Category
from apps.recipe import Recipe


class ViewTests(TestCase):
    """view module test class"""
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
        self.firstname = 'test'
        self.lastname = 'user'
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
        # print(token, "#$%^&*$%^&")
        return token

    def register_new_user(self, firstname, lastname, username, password):
        """function to register_new_user view"""
        data = {'firstname': firstname, 'lastname':lastname, \
                'username':username, 'password': password}
        response = self.client.post('/recipe/api/v1.0/user/register', data=json.dumps(data), \
                                    content_type='application/json')
        return response

    def test_register_new_user(self):
        """function to test user can register successfully"""

        response = self.register_new_user(self.firstname, self.lastname, \
                                            self.test_username, self.test_password)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Users.query.count(), 1)

    def test_user_already_exists(self):
        """function to test user already exists during dupplicate registration"""
        self.register_new_user(self.firstname, self.lastname, \
                                self.test_username, self.test_password)

        response = self.register_new_user(self.firstname, self.lastname, \
                                            self.test_username, self.test_password)
        self.assertEqual(response.status_code, 400)

    def test_missing_field_values(self):
        """function to test for missing values during user registration"""
        data = {'firstname': self.firstname, 'lastname':self.lastname, \
                'username':self.test_username}

        response = self.client.post('/recipe/api/v1.0/user/register', data=json.dumps(data), \
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_values_are_alphabet(self):
        """function to test if any value of firstname, lastname and username are not alphabets"""
        data = {'firstname': self.firstname, 'lastname':self.lastname, \
                'username':'abc123', 'password':self.test_password}

        response = self.client.post('/recipe/api/v1.0/user/register', data=json.dumps(data), \
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_password_isalphabet_only(self):
        """function to test if given password contains alphabets only"""
        data = {'firstname': self.firstname, 'lastname':self.lastname, \
                'username':self.test_username, 'password':'abcdef'}

        response = self.client.post('/recipe/api/v1.0/user/register', data=json.dumps(data), \
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_for_unauthenticated_users(self):
        """function to test for unauthorized access"""
        response = self.test_client.get('/recipe/api/v1.0/category/')
        self.assertEqual(response.status_code, 401)

    def test_login_user_ok(self):
        """function to test user login is ok"""
        self.register_new_user(self.firstname, self.lastname, \
                                            self.test_username, self.test_password)

        log_data = {"username":self.test_username, "password":self.test_password}

        response = self.client.post('/recipe/api/v1.0/user/login', data=json.dumps(log_data), \
                                        content_type='application/json')
        self.assertEqual(response.status_code, 200)


    def test_login_user_failed(self):
        """function to test user login failed"""
        self.register_new_user(self.firstname, self.lastname, \
                                            self.test_username, self.test_password)
        # log_data = {"username":self.test_username, "password":self.test_password}
        log_data = {"username":'', "password":''}
        response = self.client.post('/recipe/api/v1.0/user/login', data=json.dumps(log_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)






    def test_view_user(self):
        """function to test view_user endpoint"""
        self.register_new_user(self.firstname, self.lastname, \
                                self.test_username, self.test_password)

        response = self.test_client.get('/recipe/api/v1.0/user/view', \
                                        headers=self.get_header_token())
        self.assertEqual(response.status_code, 200)

    def test_view_user_unauthorized(self):
        """function to test user unauthorized"""
        response = self.test_client.get('/recipe/api/v1.0/user/view')
        self.assertEquals(response.status_code, 401)

    def test_invalide_view_user(self):
        "function to test no  view_user found"
        response = self.test_client.get('/recipe/api/v1.0/users/view')
        self.assertEquals(response.status_code, 404)

    def test_view_user_no_registered(self):
        "function to test no no users found"

        data = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NSwiZXhwIjoxNTE4MTcwNDA2fQ.H1zVV9_Gbkwj488nfT8D0HXTTsdrBO_e23onGIkswG4"
        token = {"x-access-token": data}

        response = self.test_client.get('/recipe/api/v1.0/users/view', \
                                        headers=token)
        self.assertEqual(response.status_code, 404)

    def test_delete_user_ok(self):
        """function to test user can be deleted"""
        self.register_new_user(self.firstname, self.lastname, \
                                self.test_username, self.test_password)

        response = self.client.delete('/recipe/api/v1.0/user/delete', \
                                        headers=self.get_header_token())
        self.assertEqual(response.status_code, 200)

    def test_delete_user_unauthorized(self):
        """function to test user not authorized to delete account"""

        response = self.client.delete('/recipe/api/v1.0/user/delete')
        self.assertEqual(response.status_code, 401)

    def test_update_user_password_ok(self):
        """function to test user password update is working"""
        self.register_new_user(self.firstname, self.lastname, \
                                self.test_username, self.test_password)

        data = {"password":"test123"}
        response = self.client.put('/recipe/api/v1.0/user/reset', data=json.dumps(data),
                                   headers=self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_update_user_no_password(self):
        """function to test password update with no new password"""
        self.register_new_user(self.firstname, self.lastname, \
                                self.test_username, self.test_password)
        data = {}

        response = self.client.put('/recipe/api/v1.0/user/reset', data=json.dumps(data),
                                   headers=self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_password_isalphabet(self):
        """function to test new password is alphabets only"""
        self.register_new_user(self.firstname, self.lastname,\
                                self.test_username, self.test_password)
        data = {"password":"testabc"}

        response = self.client.put('/recipe/api/v1.0/user/reset', data=json.dumps(data), \
                                   headers=self.get_header_token(), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_update_password_same_as_old(self):
        """function to test new password is same as old password"""
        self.register_new_user(self.firstname, self.lastname, \
                                self.test_username, self.test_password)
        data = {"password":"test1234"}

        response = self.client.put('/recipe/api/v1.0/user/reset', data=json.dumps(data), \
                                   headers=self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def create_new_category(self, user_id, name, description):
        """function to test create_new_category view"""
        data = {'user_id':user_id, 'name':name, 'description':description}

        response = self.test_client.post('/recipe/api/v1.0/category', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')

        return response

    def test_create_new_category(self):
        """function to test create_new_category view"""
        self.register_new_user(self.firstname, self.lastname, \
                               self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        response = self.create_new_category(user.id, new_category_name, description)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.query.count(), 1)

    def test_missing_fields_values(self):
        """function to test for missing values during creation of category"""
        self.register_new_user(self.firstname, self.lastname,
                               self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()

        response = self.create_new_category(user.id, 'indian food', '')
        self.assertEqual(response.status_code, 400)

    def test_category_exists(self):
        """function to test if a category exists"""
        self.register_new_user(self.firstname, self.lastname, \
                               self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        # first category values
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        # second category values
        new_category_name1 = 'local food'
        description1 = 'list of local foods'

        response = self.create_new_category(user.id, new_category_name1, description1)
        self.assertEqual(response.status_code, 400)

    def test_view_category(self):
        """function to test view_category view"""
        self.register_new_user(self.firstname, self.lastname, \
                                self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        get_response = self.test_client.get('/recipe/api/v1.0/category/', headers=\
        self.get_header_token())
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual('application/json', get_response.headers['Content-Type'])

    def test_category_search_valid(self):
        """function to test view_category search work ok"""
        self.register_new_user(self.firstname, self.lastname, \
                               self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        get_response = self.test_client.get('/recipe/api/v1.0/category/?q=f', headers=\
        self.get_header_token())
        self.assertEqual(get_response.status_code, 200)

    def test_category_search_invalid(self):
        """function to test view_category view"""
        self.register_new_user(self.firstname, self.lastname, \
                               self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        get_response = self.test_client.get('/recipe/api/v1.0/category/?q=p', headers=\
        self.get_header_token())
        self.assertEqual(get_response.status_code, 404)

    def test_invalid_view_category(self):
        """function to test view_category view"""
        self.register_new_user(self.firstname, self.lastname, \
                               self.test_username, self.test_password)

        get_response = self.test_client.get('/recipe/api/v1.0/category/?', headers=\
        self.get_header_token())
        self.assertEqual(get_response.status_code, 404)

    def test_view_category_by_id(self):
        """function to test view_category_by_id"""
        self.register_new_user(self.firstname, self.lastname, \
                                self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        get_response = self.test_client.get('/recipe/api/v1.0/category/1', headers=\
        self.get_header_token())
        self.assertEqual(get_response.status_code, 200)

    def test_category_by_invalid_id(self):
        """function to test view_category_by_id with invalid id"""
        self.register_new_user(self.firstname, self.lastname, \
                               self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        get_response = self.test_client.get('/recipe/api/v1.0/category/2', headers=\
        self.get_header_token())
        self.assertEqual(get_response.status_code, 404)

    def test_category_unauthorized_user(self):
        """function to test view_category_by_id with invalid user"""

        get_response = self.test_client.get('/recipe/api/v1.0/category/1')
        self.assertEqual(get_response.status_code, 401)

    def test_view_category_not_found(self):
        """function to test view_category_by_id badrequest"""
        self.register_new_user(self.firstname, self.lastname,\
                               self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        get_response = self.test_client.get('/recipe/api/v1.0/category/0', headers=\
        self.get_header_token())
        self.assertEqual(get_response.status_code, 404)

    def test_update_category_ok(self):
        """function to test update_category"""
        self.register_new_user(self.firstname, self.lastname,\
                                self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        update_data = {'name':'ethiopian food', 'description':'list of ethiopian food'}

        response = self.test_client.put('/recipe/api/v1.0/category/1', headers=\
        self.get_header_token(), data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_update_category_no_record(self):
        """function to test update_category no record for update"""
        self.register_new_user(self.firstname, self.lastname,\
                                self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        update_data = {'name':'ethiopian food', 'description':'list of ethiopian food'}

        response = self.test_client.put('/recipe/api/v1.0/category/2', headers=\
        self.get_header_token(), data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_category_missing(self):
        """function to test update_category variable missing """
        self.register_new_user(self.firstname, self.lastname, \
                                self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        update_data = {'name':'ethiopian food'}

        response = self.test_client.put('/recipe/api/v1.0/category/1', headers=\
        self.get_header_token(), data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_delete_category_no_record(self):
        """function to test delete_category record not found"""
        self.register_new_user(self.firstname, self.lastname, \
                               self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        response = self.test_client.delete('/recipe/api/v1.0/category/2', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_category_ok(self):
        """function to test delete_category deletes ok"""
        self.register_new_user(self.firstname, self.lastname, \
                                self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        response = self.test_client.delete('/recipe/api/v1.0/category/1', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_delete_category_not_found(self):
        """function to test update_category"""
        self.register_new_user(self.firstname, self.lastname, \
        self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        response = self.test_client.delete('/recipe/api/v1.0/category/0', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def create_new_recipe(self, category_id, name, ingredients):
        """helper function to create_new_recipe """

        data = {'category_id':category_id, 'name':name, 'ingredients':ingredients}
        response = self.test_client.post('/recipe/api/v1.0/category/recipes', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')

        return response

    def test_create_new_recipe(self):
        """function to test create_new_recipe """
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, \
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
        response = self.create_new_recipe(category.id, name, ingredients)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Recipe.query.count(), 1)

    def test_new_recipe_missing_value(self):
        """function to test create_new_recipe missing value"""
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, \
        self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        #name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        data = {'category_id':category.id, 'ingredients':ingredients}

        response = self.test_client.post('/recipe/api/v1.0/category/recipes', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_new_recipe_already_exists(self):
        """function to test create_new_recipe name already exists """
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, \
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
        self.create_new_recipe(category.id, name, ingredients)

        data = {'category_id':category.id, 'name':name, 'ingredients':ingredients}

        response = self.test_client.post('/recipe/api/v1.0/category/recipes', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_missing_recipe(self):
        """function to test update_recipe missing recipe """
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, \
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
        self.create_new_recipe(category.id, name, ingredients)

        data = {'category_id':category.id, 'ingredients':ingredients}

        response = self.test_client.put('/recipe/api/v1.0/category/recipes/2', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_update_missing_value(self):
        """function to test update_recipe missing value """
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, \
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
        self.create_new_recipe(category.id, name, ingredients)

        data = {'category_id':category.id, 'ingredients':ingredients}

        response = self.test_client.put('/recipe/api/v1.0/category/recipes/1', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_update_recipe(self):
        """function to test update_recipe value """
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, \
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
        self.create_new_recipe(category.id, name, ingredients)

        data = {'name':'coffee', 'ingredients':'coffee, sugar, hot water'}

        response = self.test_client.put('/recipe/api/v1.0/category/recipes/1', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_view_recipe(self):
        """function to test view_recipe endpoint """
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, \
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
        self.create_new_recipe(category.id, name, ingredients)

        response = self.test_client.get('/recipe/api/v1.0/category/recipes/', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_view_recipe_search_ok(self):
        """function to test view_recipe with valid search term """
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, \
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
        self.create_new_recipe(category.id, name, ingredients)

        response = self.test_client.get('/recipe/api/v1.0/category/recipes/?q=B', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_view_recipe_search_invalid(self):
        """function to test view_recipe with invalid search term """
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, \
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
        self.create_new_recipe(category.id, name, ingredients)

        response = self.test_client.get('/recipe/api/v1.0/category/recipes/?q=b', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_view_recipe_not_found(self):
        """function to test view_recipe endpoint not found"""
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, \
        self.test_username, self.test_password)

        response = self.test_client.get('/recipe/api/v1.0/category/recipes/', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_view_recipe_bad_request(self):
        """function to test view_recipe endpoint with bad request"""
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, self.test_username, \
        self.test_password)

        response = self.test_client.get('/recipe/api/v1.0/category/recipes/0', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_view_recipe_unauthorized(self):
        """function to test view_recipe by category id endpoint unauthorized"""
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, self.test_username, \
        self.test_password)
        self.register_new_user('James', 'Alule', 'jlule', 'j1234')
        user = Users.query.filter_by(username='jlule').first()
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        self.create_new_recipe(category.id, name, ingredients)

        response = self.test_client.get('/recipe/api/v1.0/category/recipes/1')
        self.assertEqual(response.status_code, 401)

    def test_view_recipe_no_content(self):
        """function to test view_recipe by category id endpoint no content found"""
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, self.test_username, \
        self.test_password)
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(2, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        self.create_new_recipe(category.id, name, ingredients)

        response = self.test_client.get('/recipe/api/v1.0/category/recipes/2', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_view_recipe_by_category_ok(self):
        """function to test view_recipe by category id"""
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, self.test_username, \
        self.test_password)
        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(2, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        self.create_new_recipe(category.id, name, ingredients)

        response = self.test_client.get('/recipe/api/v1.0/category/recipes/1', headers=\
       self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_view_recipe_by_category_recipe_ok(self):
        """function to test view_recipe by category id"""
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, self.test_username, \
        self.test_password)

        #creatng category for the user
        category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(2, category_name, description)
        #creating recipe of the category
        category = Category.query.filter_by(name=category_name).first()
        name = 'Black Tea'
        ingredients = 'Tea leave, sugar, hot water'
        self.create_new_recipe(category.id, name, ingredients)

        response = self.test_client.get('/recipe/api/v1.0/category/1/recipes/1', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_view_recipe_no_category_no_recipe(self):
        """function to test view_recipe with no category id and no recipe id"""
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, self.test_username, \
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
        self.create_new_recipe(category.id, name, ingredients)

        response = self.test_client.get('/recipe/api/v1.0/category/1/recipes/2', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_delete_recipe_by_id_bad_request(self):
        """function to test view_recipe with no category and recipe found"""
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, self.test_username, \
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
        self.create_new_recipe(category.id, name, ingredients)

        response = self.test_client.delete('/recipe/api/v1.0/category/recipes/0', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_delete_recipe_no_content(self):
        """function to test view_recipe with no category and recipe found"""
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, self.test_username, \
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
        self.create_new_recipe(category.id, name, ingredients)

        response = self.test_client.delete('/recipe/api/v1.0/category/recipes/3', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_recipe_by_id_ok(self):
        """function to test view_recipe with no category and recipe found"""
        #registering recipe user
        self.register_new_user(self.firstname, self.lastname, self.test_username, \
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
        self.create_new_recipe(category.id, name, ingredients)

        response = self.test_client.delete('/recipe/api/v1.0/category/recipes/1', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 200)

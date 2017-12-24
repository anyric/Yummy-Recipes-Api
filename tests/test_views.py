""" module to test views.py"""
import unittest
from flask_testing import TestCase
from base64 import b64encode
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
        self.header = Headers()
        db.create_all()

    def tearDown(self):
        """function to delete test_db after every test case"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_authentication_header(self):
        """function to retrieve auth header"""
        auth_data = b64encode(b'testuser:test1234').decode('utf-8')

        self.header.add('Authorization', 'Basic ' + auth_data)
        self.header.add('Content-Type', 'application/json')
        return self.header

    def register_new_user(self, firstname, lastname, username, password):
        """function to register_new_user view"""
        data = {'firstname': firstname, 'lastname':lastname, 'username':username, 'password': password}
        response = self.client.post('/recipe/api/v1.0/user', data=json.dumps(data), content_type='application/json')
        return response

    def test_regiter_new_user(self):
        """function to test user can register successfully"""
        response = self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Users.query.count(), 1)

    def test_user_already_exists(self):
        """function to test user already exists during dupplicate registration"""
        self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)

        response = self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)
        self.assertEqual(response.status_code, 400)

    def test_missing_field_values(self):
        """function to test for missing values during user registration"""
        data = {'firstname': self.firstname, 'lastname':self.lastname, 'username':self.test_username}

        response = self.client.post('/recipe/api/v1.0/user', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_values_are_alphabet(self):
        """function to test if any value of firstname, lastname and username are not alphabets"""
        data = {'firstname': self.firstname, 'lastname':self.lastname, 'username':'abc123', 'password':self.test_password}

        response = self.client.post('/recipe/api/v1.0/user', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_password_isalphabet_only(self):
        """function to test if given password contains alphabets only"""
        data = {'firstname': self.firstname, 'lastname':self.lastname, 'username':self.test_username, 'password':'abcdef'}

        response = self.client.post('/recipe/api/v1.0/user', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_for_unauthenticated_users(self):
        """function to test for unauthorized access"""
        response = self.test_client.get('/recipe/api/v1.0/category/')
        self.assertEqual(response.status_code, 401)

    def test_view_user(self):
        """function to test view_user endpoint"""
        self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)

        response = self.test_client.get('/recipe/api/v1.0/user')
        self.assertEquals(response.status_code, 200)

    def test_no_registered_user(self):
        """function to test no registered user"""
        # self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)

        response = self.test_client.get('/recipe/api/v1.0/user')
        self.assertEquals(response.status_code, 204)

    def test_view_no_registered_user(self):
        "function to test no user registered"
        response = self.test_client.get('/recipe/api/v1.0/user')
        self.assertEquals(response.status_code, 204)

    def test_invalide_view_user(self):
        "function to test no  view_user found"
        response = self.test_client.get('/recipe/api/v1.0/users')
        self.assertEquals(response.status_code, 404)

    def create_new_category(self, user_id, name, description):
        """function to test create_new_category view"""
        data = {'user_id':user_id, 'name':name, 'description':description}

        response = self.test_client.post('/recipe/api/v1.0/category', headers=\
        self.get_authentication_header(), data=json.dumps(data))
        return response

    def test_create_new_category(self):
        """function to test create_new_category view"""
        self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        response = self.create_new_category(user.id, new_category_name, description)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.query.count(), 1)

    def test_missing_fields_values(self):
        """function to test for missing values during creation of category"""
        self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()

        response = self.create_new_category(user.id, 'indian food', '')
        self.assertEqual(response.status_code, 400)

    def test_category_exit(self):
        """function to test if a category exists"""
        self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)

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
        self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        get_response = self.test_client.get('/recipe/api/v1.0/category/', headers=\
        self.get_authentication_header())
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual('application/json', get_response.headers['Content-Type'])

    def test_category_search_valid(self):
        """function to test view_category search work ok"""
        self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        get_response = self.test_client.get('/recipe/api/v1.0/category/?q=f', headers=\
        self.get_authentication_header())
        self.assertEqual(get_response.status_code, 200)

    def test_category_search_invalid(self):
        """function to test view_category view"""
        self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        get_response = self.test_client.get('/recipe/api/v1.0/category/?q=p', headers=\
        self.get_authentication_header())
        self.assertEqual(get_response.status_code, 204)

    def test_invalid_view_category(self):
        """function to test view_category view"""
        self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)

        get_response = self.test_client.get('/recipe/api/v1.0/category/?', headers=\
        self.get_authentication_header())
        self.assertEqual(get_response.status_code, 404)

    def test_view_category_by_id(self):
        """function to test view_category_by_id"""
        self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        get_response = self.test_client.get('/recipe/api/v1.0/category/1', headers=\
        self.get_authentication_header())
        self.assertEqual(get_response.status_code, 200)

    def test_category_by_invalid_id(self):
        """function to test view_category_by_id with invalid id"""
        self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        get_response = self.test_client.get('/recipe/api/v1.0/category/2', headers=\
        self.get_authentication_header())
        self.assertEqual(get_response.status_code, 204)

    def test_category_unauthorized_user(self):
        """function to test view_category_by_id with invalid user"""
        # self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)
        self.register_new_user('James', 'Alule', 'jlule', 'j1234')

        user = Users.query.filter_by(username='jlule').first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        get_response = self.test_client.get('/recipe/api/v1.0/category/1', headers=\
        self.get_authentication_header())
        self.assertEqual(get_response.status_code, 401)

    def test_view_category_not_found(self):
        """function to test view_category_by_id badrequest"""
        self.register_new_user(self.firstname, self.lastname, self.test_username, self.test_password)

        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'

        self.create_new_category(user.id, new_category_name, description)

        get_response = self.test_client.get('/recipe/api/v1.0/category/0', headers=\
        self.get_authentication_header())
        self.assertEqual(get_response.status_code, 404)

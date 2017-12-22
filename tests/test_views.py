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

    def test_for_unauthenticated_users(self):
        """function to test for unauthorized access"""
        response = self.test_client.get('/recipe/api/v1.0/category/')
        self.assertEqual(response.status_code, 401)

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
        print(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.query.count(), 1)


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


"""module to test category view"""
from flask_testing import TestCase
import json

from apps import app, db
from apps import config
from apps.models.category import Category
from apps.models.user import Users

class CategoryTests(TestCase):
    """class to test category views"""
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
        """function to test create_new_category view"""
        data = {'user_id':user_id, 'name':name, 'description':description}
        response = self.test_client.post('/recipe/api/v1.0/category', headers=\
        self.get_header_token(), data=json.dumps(data), content_type='application/json')
        return response

    def test_create_new_category(self):
        """function to test create_new_category view"""
        self.register_new_user(self.name, self.email, \
                               self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'
        response = self.create_new_category(user.id, new_category_name, description)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.query.count(), 1)

    def test_missing_fields_values(self):
        """function to test for missing values during creation of category"""
        self.register_new_user(self.name, self.email,
                               self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        response = self.create_new_category(user.id, 'indian food', '')
        self.assertEqual(response.status_code, 400)

    def test_category_exists(self):
        """function to test if a category exists"""
        self.register_new_user(self.name, self.email, \
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
        self.register_new_user(self.name, self.email, \
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
        self.register_new_user(self.name, self.email, \
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
        self.register_new_user(self.name, self.email, \
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
        self.register_new_user(self.name, self.email, \
                               self.test_username, self.test_password)
        get_response = self.test_client.get('/recipe/api/v1.0/category/?', headers=\
        self.get_header_token())
        self.assertEqual(get_response.status_code, 404)

    def test_view_category_by_id(self):
        """function to test view_category_by_id"""
        self.register_new_user(self.name, self.email, \
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
        self.register_new_user(self.name, self.email, \
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
        self.register_new_user(self.name, self.email,\
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
        self.register_new_user(self.name, self.email,\
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
        self.register_new_user(self.name, self.email,\
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
        self.register_new_user(self.name, self.email, \
                                self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, new_category_name, description)
        update_data = {'name':'ethiopian food', 'description':''}
        response = self.test_client.put('/recipe/api/v1.0/category/1', headers=\
        self.get_header_token(), data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_delete_category_no_record(self):
        """function to test delete_category record not found"""
        self.register_new_user(self.name, self.email, \
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
        self.register_new_user(self.name, self.email, \
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
        self.register_new_user(self.name, self.email, \
        self.test_username, self.test_password)
        user = Users.query.filter_by(username=self.test_username).first()
        new_category_name = 'local food'
        description = 'list of local foods'
        self.create_new_category(user.id, new_category_name, description)
        response = self.test_client.delete('/recipe/api/v1.0/category/0', headers=\
        self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 404)

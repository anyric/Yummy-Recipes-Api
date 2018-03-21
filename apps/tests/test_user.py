""" module to test user views.py"""
from flask_testing import TestCase
import json

from apps import app, db
from apps.utilities import config
from apps.models.user import Users

class UserTests(TestCase):
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
        data = {'name': name, 'email':email, 'username':username, 'password': password}
        response = self.client.post('/recipe/api/v1.0/user/register', data=json.dumps(data), \
                                    content_type='application/json')
        return response

    def test_register_new_user(self):
        """function to test user can register successfully"""
        response = self.register_new_user(self.name, self.email, \
        self.test_username, self.test_password)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Users.query.count(), 1)

    def test_wrong_email(self):
        """function to test wrong email"""
        response = self.register_new_user(self.name, "testexample.com", \
        self.test_username, self.test_password)
        self.assertEqual(response.status_code, 400)

    def test_user_already_exists(self):
        """function to test user already exists during dupplicate registration"""
        self.register_new_user(self.name, self.email, \
                                self.test_username, self.test_password)
        response = self.register_new_user(self.name, self.email, \
        self.test_username, self.test_password)
        self.assertEqual(response.status_code, 400)

    def test_missing_field_values(self):
        """function to test for missing values during user registration"""
        data = {'name': self.name, 'email':self.email, 'username':self.test_username, 'password':''}
        response = self.client.post('/recipe/api/v1.0/user/register', data=json.dumps(data), \
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_values_are_alphabet(self):
        """function to test if any value of firstname, lastname and username are not alphabets"""
        data = {'name': self.name, 'email':self.email, \
                'username':'abc123', 'password':self.test_password}
        response = self.client.post('/recipe/api/v1.0/user/register', data=json.dumps(data), \
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_password_isalphabet_only(self):
        """function to test if given password contains alphabets only"""
        data = {'name': self.name, 'email':self.email, \
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
        self.register_new_user(self.name, self.email, self.test_username, self.test_password)
        log_data = {"username":self.test_username, "password":self.test_password}
        response = self.client.post('/recipe/api/v1.0/user/login', data=json.dumps(log_data), \
                                        content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_login_user_failed(self):
        """function to test user login failed"""
        self.register_new_user(self.name, self.email, self.test_username, self.test_password)
        log_data = {"username":'', "password":''}
        response = self.client.post('/recipe/api/v1.0/user/login', data=json.dumps(log_data), \
        content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_wrong_values(self):
        """function to test user login failed"""
        self.register_new_user(self.name, self.email, self.test_username, self.test_password)
        log_data = {"username":'tester', "password":'test123'}
        response = self.client.post('/recipe/api/v1.0/user/login', data=json.dumps(log_data), \
        content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_view_user(self):
        """function to test view_user endpoint"""
        self.register_new_user(self.name, self.email, self.test_username, self.test_password)
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
        "function to test no users found"
        data = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NSwiZXhwIjoxNTE4MTcwNDA2fQ.H1zVV9_Gbkwj488nfT8D0HXTTsdrBO_e23onGIkswG4"
        token = {"x-access-token": data}
        response = self.test_client.get('/recipe/api/v1.0/users/view', \
                                        headers=token)
        self.assertEqual(response.status_code, 404)

    def test_delete_user_ok(self):
        """function to test user can be deleted"""
        self.register_new_user(self.name, self.email, \
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
        self.register_new_user(self.name, self.email, \
                                self.test_username, self.test_password)
        data = {"email":"testuser@example.com", "password":"test123"}
        response = self.client.put('/recipe/api/v1.0/user/reset', data=json.dumps(data),
                                   headers=self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_update_user_no_password(self):
        """function to test password update with no new password"""
        self.register_new_user(self.name, self.email, \
                                self.test_username, self.test_password)
        data = {}
        response = self.client.put('/recipe/api/v1.0/user/reset', data=json.dumps(data),
                                   headers=self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_password_isalphabet(self):
        """function to test new password is alphabets only"""
        self.register_new_user(self.name, self.email,\
                                self.test_username, self.test_password)
        data = {"email":self.email, "password":"testabc"}
        response = self.client.put('/recipe/api/v1.0/user/reset', data=json.dumps(data), \
                                   headers=self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_password_same_as_old(self):
        """function to test new password is same as old password"""
        self.register_new_user(self.name, self.email, \
                                self.test_username, self.test_password)
        data = {"email":self.email, "password":"test1234"}
        response = self.client.put('/recipe/api/v1.0/user/reset', data=json.dumps(data), \
                                   headers=self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_wrong_email(self):
        """function to test wrong email"""
        self.register_new_user(self.name, self.email, self.test_username, self.test_password)
        data = {"email":"testexample.com", "password":"test1234"}
        response = self.client.put('/recipe/api/v1.0/user/reset', data=json.dumps(data), \
                                   headers=self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_logout_ok(self):
        """function to test user logout"""
        self.register_new_user(self.name, self.email, self.test_username, self.test_password)
        log_data = {"username":self.test_username, "password":self.test_password}
        self.client.post('/recipe/api/v1.0/user/login', data=json.dumps(log_data), \
                                        content_type='application/json')
        response = self.client.post('/recipe/api/v1.0/user/logout', \
        headers=self.get_header_token(), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_logout_failed(self):
        """function to test user logout"""
        self.register_new_user(self.name, self.email, self.test_username, self.test_password)
        log_data = {"username":self.test_username, "password":self.test_password}
        self.client.post('/recipe/api/v1.0/user/login', data=json.dumps(log_data), \
                                        content_type='application/json')
        self.client.post('/recipe/api/v1.0/user/logout', \
        headers=self.get_header_token(), content_type='application/json')
        response = self.client.post('/recipe/api/v1.0/user/logout', \
        headers=self.get_header_token(), content_type='application/json')
        response_data = json.dumps(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 401)

import unittest
# import json
from flask import jsonify
from apps import app, db, config

class AuthTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        config_name = config.TestingConfig
        app.config.from_object(config_name)
        self.app = app
        # initialize the test client
        self.client = self.app.test_client
        # This is the user test json data with a predefined email and password
        self.user_data = {
            'firstname': 'test',
            'lastname':'user',
            'username':'testuser',
            'password': '1234'
        }

        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_user_registration(self):
        """Test user registration works correcty."""
        data = jsonify(self.user_data)
        res = self.client().post('/new_user', data=data, content_type='application/json')
        # get the results returned in json format
        # result = json.loads(res.data.decode())
        # assert that the request contains a success message and a 201 status code
        # self.assertEqual(result['message'], "You registered successfully.")
        self.assertEqual(res.status_code, 201)

    def test_user_already_registered(self):
        """Test that a user cannot be registered twice."""
        data = jsonify(self.user_data)
        res = self.client().post('/recipe/api/v1.0/user', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        second_res = self.client().post('/recipe/api/v1.0/user', data=data, content_type='application/json')
        self.assertEqual(second_res.status_code, 202)
        # get the results returned in json format
        # result = json.loads(second_res.data.decode())
        # self.assertEqual(
            # result['message'], "User already exists. Please login.")

    def tearDown(self):
        db.session.remove()
        db.drop_all()

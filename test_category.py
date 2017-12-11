"""test for category.py"""
import unittest
import json
from app import app, db

class CategoryTestCase(unittest.TestCase):
    """This class represents the category test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = app
        self.client = self.app.test_client
        self.category = {'user_id':1, 'name': 'Local food',
                         'description':'Collection of local recipes'}

        # binding app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_category_creation(self):
        """Test API can create a category through POST request"""
        response = self.client().post('/category', data=self.category)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Local food', str(response.data))

    def test_category_retrieval(self):
        """Test API can retrieve a category through GET request."""
        response = self.client().post('/category', data=self.category)
        self.assertEqual(response.status_code, 201)
        response = self.client().get('/category')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Local food', str(response.data))

    def test_category_retrieval_by_name(self):
        """Test API can retrieval a category by using it's name."""
        response = self.client().post('/category/', data=self.category)
        self.assertEqual(response.status_code, 201)
        result_in_json = json.loads(response.data.decode('utf-8').replace("'", "\""))
        result = self.client().get('/category/{}'.format(result_in_json['name']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Local food', str(result.data))

    def test_category_update(self):
        """Test API can update an existing category through PUT request"""
        category = {'user_id':1, 'name': 'Indian food',
                    'description':'Collection of indian recipes'}
        response = self.client().post('/category/', data=category)
        self.assertEqual(response.status_code, 201)

        category = {'old_name': 'Indian food', 'new_name':'Italian food',
                    'description':'Collection of italian recipes'}
        response = self.client().put('/category/1', data=category)
        self.assertEqual(response.status_code, 200)
        results = self.client().get('/category/1')
        self.assertIn('Italian food', str(results.data))

    def test_category_deletion(self):
        """Test API can delete an existing category through DELETE request"""
        category = {'user_id':1, 'name': 'Indian food',
                    'description':'Collection of indian recipes'}
        response = self.client().post('/category/', data=category)
        self.assertEqual(response.status_code, 201)
        response = self.client().delete('/category/1')
        self.assertEqual(response.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/category/1')
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # deletes all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

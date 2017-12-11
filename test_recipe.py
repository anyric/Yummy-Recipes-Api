"""test for category.py"""
import unittest
import json
from app import app, db

class RecipeTestCase(unittest.TestCase):
    """This class represents the recipe test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = app
        self.client = self.app.test_client
        self.recipe = {'category_id':1, 'name': 'molokonyi',
                         'description':'source made from cow legs'}

        # binding app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_recipe_creation(self):
        """Test API can create a recipe through POST request"""
        response = self.client().post('/recipe', data=self.recipe)
        self.assertEqual(response.status_code, 201)
        self.assertIn('molokonyi', str(response.data))

    def test_recipe_retrieval(self):
        """Test API can retrieve a recipe through GET request."""
        response = self.client().post('/recipe', data=self.recipe)
        self.assertEqual(response.status_code, 201)
        response = self.client().get('/recipe')
        self.assertEqual(response.status_code, 200)
        self.assertIn('molokonyi', str(response.data))

    def test_recipe_retrieval_by_name(self):
        """Test API can retrieval a recipe by using it's name."""
        response = self.client().post('/recipe/', data=self.recipe)
        self.assertEqual(response.status_code, 201)
        result_in_json = json.loads(response.data.decode('utf-8').replace("'", "\""))
        result = self.client().get('/recipe/{}'.format(result_in_json['name']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('molokonyi', str(result.data))

    def test_recipe_update(self):
        """Test API can update an existing recipe through PUT request"""
        category = {'category_id':1,'name': 'Green', 
                     'description':'Source made from vegetable leaves'}
        response = self.client().post('/category/', data=category)
        self.assertEqual(response.status_code, 201)

        category = {'old_name': 'Green', 'new_name':'Cabbage',
                    'description':'Source made from cabbage vegetables'}
        response = self.client().put('/category/1', data=category)
        self.assertEqual(response.status_code, 200)
        results = self.client().get('/category/1')
        self.assertIn('Cabbage', str(results.data))

    def test_recipt_deletion(self):
        """Test API can delete an existing recipe through DELETE request"""
        category = {'category_id':1, 'name': 'Cabbage',
                    'description':'source made from cabbage vegetables'}
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

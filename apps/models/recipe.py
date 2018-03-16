""" module to manage recipe"""
from datetime import datetime
from marshmallow import Schema, fields, pre_load
from marshmallow import validate
from flask_marshmallow import Marshmallow

from apps import db, ma
# from apps.models.category import Category

class Recipe(db.Model):
    """model to store recipes"""
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)
    category_id = db.Column('category_id', db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'))
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    date_modified = db.Column(db.DateTime, nullable=False)

    def __init__(self, category_id, user_id, name, incredients):
        self.category_id = category_id
        self.user_id = user_id
        self.name = name
        self.ingredients = incredients
        self.date_modified = datetime.utcnow()
    
    def save(self):
        """method to store new recipe"""
        db.session.add(self)
        db.session.commit()

    def update_recipe(self, recipe_name, ingredients):
        """method to update recipe"""
        self.name = recipe_name
        self.ingredients = ingredients
        self.date_modified = datetime.utcnow()
        self.save()


    def get_all(self, category_id):
        """method to retrieve all recipes of a given category"""
        return Recipe.query.filter_by(category_id=category_id).all()
    @staticmethod
    def get_recipe_category_id(category_id, current_user):
        """method to retrieve all recipes of a given category and user id"""
        recipes = Recipe.query.filter(Recipe.category_id == category_id, \
        Recipe.user_id == current_user.id).all()
        return recipes

    @staticmethod
    def get_recipe_by_id(recipe_id, current_user):
        """method to retrieve all recipes of a given category and user id"""
        recipe = Recipe.query.filter(Recipe.id == recipe_id, \
        Recipe.user_id == current_user.id).first()
        return recipe
    @staticmethod
    def get_by_recipe_category_id(category_id, recipe_id, current_user):
        """method to retrieve all recipes of a given category and user id"""
        recipe = Recipe.query.filter(Recipe.category_id == category_id, Recipe.id == recipe_id, \
        Recipe.user_id == current_user.id).first()
        return recipe


    def delete(self):
        """method to delete a recipe"""
        db.session.delete(self)
        db.session.commit()

class RecipeSchema(ma.Schema):
    """class to create recipe model for pagination"""
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(1))
    ingredients = fields.String(required=True, validate=validate.Length(1))
    category_id = fields.Integer()
    user_id = fields.Integer()
    date_modified = fields.DateTime()
    url = ma.URLFor('view_recipe', id='<id>', _external=True)

    @pre_load
    def process_recipe(self, data):
        """method to process the recipe data"""
        recipe = data.get('recipe')
        if recipe:
            if isinstance(recipe, dict):
                recipe_name = recipe.get('name')
            else:
                recipe_name = recipe
            recipe_dict = dict(name=recipe_name)
        else:
            recipe_dict = {}
        data['recipe'] = recipe_dict
        return data

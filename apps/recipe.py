""" module to manage recipe"""
from apps import db
from apps.category import Category
class Recipe(db.Model):
    """model to store recipes"""
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    incredients = db.Column(db.String(60), nullable=False)
    category_id = db.Column('category_id', db.Integer, db.ForeignKey('category.id'))

    def __init__(self, category_id, name, incredients):
        self.category_id = category_id
        self.name = name
        self.incredients = incredients

    def save(self):
        """method to store new recipe"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def getrecipe(category_id):
        """method to retrieve recipe"""
        recipes = Recipe.query.filter_by(category_id=category_id).first()
        category = Category.query.filter_by(id=category_id).first()
        results = []

        for recipe in recipes:
            obj = {
                'id': recipe.id,
                'name': recipe.name,
                'category': category.name,
                'incredients': recipe.incredients
                }
            results.append(obj)

        return results

    def delete(self):
        """method to delete a recipe"""
        db.session.delete(self)
        db.session.commit()


    def __repr__(self):
        return 'name {}'.format(self.name)




"""
class Recipe():
    #class to manipulate recipes

    def __init__(self):



    def createrecipe(self, user_id, name, description):
        #insert recipe into the recipes table
        recipe = models.Recipe(user_id, name, description)
        db.session.add(recipe)
        db.session.commit()


    def viewrecipe(self, user_id):
        #function to view user recipe
        recipes = models.Recipe.query.filter_by(user_id=user_id)
        results = []
        for recipe in recipes:
            result = dict(recipe_name=recipe.name, recipe_id=recipe.id)
            results.append(result)
        return results

    def getrecipe(self, name):
        #function to get recipe
        recipe = models.Recipe.query.filter_by(name=name).first_or_404()
        return recipe


    def updaterecipe(self, recipe, name, decription):
        #function to uodate recipe details
        recipe_item = models.Recipe.query.get(recipe.id)
        recipe_item.name = name
        recipe_item.description = decription
        db.session.commit()


    def deleterecipe(self, name):
        #function to delete a recipe in database
        recipe = models.Recipe.query.filter_by(name=name).first()
        db.session.delete(recipe)
        db.session.commit()
"""

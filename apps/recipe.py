""" module to manage recipe"""
from apps import db
from apps.category import Category
class Recipe(db.Model):
    """model to store recipes"""
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)
    category_id = db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
    date_modified = db.Column(db.DateTime, nullable=False)

    def __init__(self, category_id, name, incredients, date_modified):
        self.category_id = category_id
        self.name = name
        self.ingredients = incredients
        self.date_modified = date_modified

    def save(self):
        """method to store new recipe"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def getrecipe(category_id):
        """method to retrieve recipe"""
        recipes = Recipe.query.filter_by(category_id=category_id)
        category = Category.query.filter_by(id=category_id).first()
        results = []
        if recipes:
            for recipe in recipes:
                obj = {
                    'id': recipe.id,
                    'name': recipe.name,
                    'category': category.name,
                    'ingredients': recipe.ingredients,
                    'Date_modified':recipe.date_modified
                    }
                results.append(obj)
                return results

        return {"message":"No recipe found"}

    def delete(self):
        """method to delete a recipe"""
        db.session.delete(self)
        db.session.commit()


    def __repr__(self):
        return 'name {}'.format(self.name)

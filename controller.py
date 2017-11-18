"""module to manage the model class"""
from app import db
from models import Users, Category, Recipe

db.create_all()


def createuser(firstname, lastname, username, password):
    """insert user into the user table"""
    user = Users(firstname, lastname, username, password)
    db.session.add(user)
    db.session.commit()

def getuser(username):
    """function to get login user id"""
    user = Users.query.filter_by(username=username).first_or_404()
    return user

def createcategory(user_id, name, description):
    """insert category into the category table"""
    category = Category(user_id, name, description)
    db.session.add(category)
    db.session.commit()

def viewcategory(user_id):
    """function to view user recipe category"""
    category = Category.query.filter(user_id=user_id).all()
    return category

def updatecategory(category_id, name, description):
    """function to update category details"""
    category_item = Category.query.get(category_id)
    category_item.name = name
    category_item.description = description
    db.session.commit()

def deletecategory(name):
    """function to delete a category in database"""
    category = Category.query.filter_by(name=name).first()
    db.session.delete(category)
    db.session.commit()


def createrecipe(user_id, name, description):
    """insert recipe into the recipes table"""
    recipe = Recipe(user_id, name, description)
    db.session.add(recipe)
    db.session.commit()


def viewrecipe(user_id):
    """function to view user recipe"""
    recipe = Recipe.query.filter(user_id=user_id).all()
    return recipe

def updaterecipe(recipe_id, name, description):
    """function to update recipe details"""
    recipe_item = Category.query.get(recipe_id)
    recipe_item.name = name
    recipe_item.description = description
    db.session.commit()

def deleterecipe(name):
    """function to delete a recipe in database"""
    recipe = Recipe.query.filter_by(name=name).first()
    db.session.delete(recipe)
    db.session.commit()
#createuser('Richard', 'Anyama', 'cooldad', 'colpass')
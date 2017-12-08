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
    """function to get login user"""
    user = Users.query.filter_by(username=username).first_or_404()
    return user

def createcategory(user_id, name, description):
    """insert category into the category table"""
    category = Category(user_id, name, description)
    db.session.add(category)
    db.session.commit()

def viewcategory(user_id):
    """function to view user recipe category"""
    categories = Category.query.filter_by(user_id=user_id)
    results = []
    for category in categories:
        result = dict(category_name=category.name, category_id=category.id, category_description=category.description, user=user_id)
        results.append(result)
    return results


def getcategory(name):
    """function to get recipe category"""
    category = Category.query.filter_by(name=name).first_or_404()
    return category


def updatecategory(category, name, decription):
    """function to uodate category details"""
    category_item = Category.query.get(category.id)
    category_item.name = name
    category_item.description = decription
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
    recipes = Recipe.query.filter_by(user_id=user_id)
    results = []
    for recipe in recipes:
        result = dict(recipe_name=recipe.name, recipe_id=recipe.id)
        results.append(result)
    return results

def getrecipe(name):
    """function to get recipe"""
    recipe = Recipe.query.filter_by(name=name).first_or_404()
    return recipe


def updaterecipe(recipe, name, decription):
    """function to uodate recipe details"""
    recipe_item = Recipe.query.get(recipe.id)
    recipe_item.name = name
    recipe_item.description = decription
    db.session.commit()


def deleterecipe(name):
    """function to delete a recipe in database"""
    recipe = Recipe.query.filter_by(name=name).first()
    db.session.delete(recipe)
    db.session.commit()

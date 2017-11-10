from flask_sqlalchemy import SQLAlchemy
import datetime

database = SQLAlchemy()

class BaseDataModel(database.Model):
    """Base data model from which other models inherit"""
    __abstract__ = True

    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        """Define a base way to print models"""
        return '%s(%s)' % (self.__class__.__name__, {
            column: value
            for column, value in self._to_dict().items()
        })

    def json(self):
        """
                Define a base way to jsonify models, dealing with datetime objects
        """
        return {
            column: value if not isinstance(value, datetime.date) else value.strftime('%Y-%m-%d')
            for column, value in self._to_dict().items()
        }



class User(BaseDataModel, database.Model):
    """Model for the users table"""
    __tablename__ = 'users'

    id = database.Column(database.Integer, primary_key = True)
    name = database.Column(database.varchar)
    username = database.Column(database.varchar)
    password = database.Column(database.password)


class Category(BaseDataModel, database.Model):
    """Model for the category table"""
    __tablename__ = 'category'

    id = database.Column(database.Integer, primary_key = True)
    categoryname = database.Column(database.varchar)
    description = database.Column(database.varchar)


class Recipe(BaseDataModel, database.Model):
    """Model for the recipe table"""
    __tablename__ = 'recipe'

    id = database.Column(database.Integer, primary_key = True)
    recipename = database.Column(database.varchar)
    description = database.Column(database.varchar)
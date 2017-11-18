"""module to create data models"""

from app import db

class Users(db.Model):
    """model to store user details """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, firstname, lastname, username, password):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = password

    def __repr__(self):
        return '<username {}'.format(self.username)


class Category(db.Model):
    """model to store recipe categroy"""
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    description = db.Column(db.String(60), nullable=False)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'))

    def __init__(self, user_id, name, description):
        self.user_id = user_id
        self.name = name
        self.description = description

    def __repr__(self):
        return '<title {}'.format(self.name)


class Recipe(db.Model):
    """model to store recipes"""
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    description = db.Column(db.String(60), nullable=False)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'))

    def __init__(self, user_id, name, description):
        self.user_id = user_id
        self.name = name
        self.description = description

    def __repr__(self):
        return '<title {}'.format(self.name)

""" module to manage users"""
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

    def save(self):
        """method to store new user"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def getusers():
        """method to retrieve users"""
        user = Users.query.all()
        return user

    def delete(self):
        """method to delete a user"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return 'username {}'.format(self.username)

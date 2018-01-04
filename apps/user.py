""" module to manage users"""
from apps import db

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
        userlist = Users.query.all()
        results = []

        for user in userlist:
            obj = {
                'id': user.id,
                'firstname': user.firstname,
                'lastname':user.lastname,
                'username': user.username
                }
            results.append(obj)

        return results


    def delete(self):
        """method to delete a user"""
        db.session.delete(self)
        db.session.commit()

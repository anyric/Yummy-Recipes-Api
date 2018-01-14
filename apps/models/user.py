""" module to manage users"""
import datetime
import jwt
from apps import db, app

class Users(db.Model):
    """model to store user details """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, name, email, username, password):
        self.name = name
        self.email = email
        self.username = username
        self.password = password

    def save(self):
        """method to store new user"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def getuser(current_user):
        """method to retrieve users"""
        userlist = Users.query.filter_by(id=current_user.id).first()
        results = {}
        if userlist:
            results["id"] = userlist.id
            results["name"] = userlist.name
            results["email"] = userlist.email
            results["username"] = userlist.username

        return results


    def delete(self):
        """method to delete a user"""
        db.session.delete(self)
        db.session.commit()

class BlacklistTokens(db.Model):
    """model to store blacklisted tokens """
    __tablename__ = 'blacklist'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False)
    date_blacklisted = db.Column(db.DateTime, nullable=False)


    def __init__(self, token):
        self.token = token
        self.date_blacklisted = datetime.datetime.utcnow()

    def save(self):
        """method to store new user"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def verify_blacklist(token):
        """method to verify if token is blacklisted """
        blacklisted = BlacklistTokens.query.filter_by(token=token).first()
        if blacklisted:
            return True
        else:
            return False
    @staticmethod
    def generate_token(user_id):
        """method to generate token"""
        token = jwt.encode(
            {'id':user_id, 'exp':datetime.datetime.utcnow()+ datetime.timedelta(hours=720)},
            app.config['SECRET'])#expires after 30 days

        return token

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

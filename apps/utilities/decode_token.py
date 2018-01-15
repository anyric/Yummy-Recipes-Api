"""view endpoint module that allow user to interact with the system"""
from flask import jsonify, request
import jwt
from functools import wraps

from apps import app
from apps.models.user import Users

def token_required(function):
    """function to retrieve token from request header"""
    @wraps(function)
    def decorated(*args, **kwargs):
        """function to decode to token from the request header"""
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({"message":"Token is missing!"}), 401

        user_data = jwt.decode(token, app.config['SECRET'])
        if user_data:
            current_user = Users.query.filter_by(id=user_data['id']).first()
        else:
            return jsonify({"message":"Token is invalid!"}), 401

        return function(current_user, *args, **kwargs)
    return decorated

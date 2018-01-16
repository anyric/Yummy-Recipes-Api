"""module for user endpoints"""
import re
from flask import request, jsonify, g, make_response, json
from flasgger import swag_from

from apps.models.user import Users, BlacklistTokens
from apps import app
from apps.utilities.decode_token import token_required

@app.route('/recipe/api/v1.0/user/register', methods=['POST'])
def register_new_user():
    """function to create new user"""
    data = request.get_json()
    name = str(data['name']).strip()
    email = str(data['email']).strip()
    username = str(data['username']).strip()
    password = str(data['password']).strip()
    if name and email and username and password:
        if re.match(r'[a-zA-Z0-9.-_]+@[a-z]+\.[a-z]+', email):
            if password.isalpha():
                return jsonify({"message":"Password can't be only alphabets"}), 400
            if not isinstance(name, str) or not username.isalpha():
                return jsonify({"message":"Name and username must be only alphabets"}), 400
            user_exit = Users.query.filter_by(username=username).first()
            if user_exit:
                return jsonify({"message":"username {} already exits!".format(username)}), 400
            else:
                user = Users(name, email, username, password)
                user.save()
                response = jsonify({'message': "user {} registered successfully!".\
                                    format(user.username)}), 201
                return response
        else:
            return jsonify({"message":"wrong email format!"}), 400
    return jsonify({"message":"Please fill in all fields"}), 400

@app.route('/recipe/api/v1.0/user/reset', methods=['PUT'])
@swag_from("/apps/docs/updateuserpassword.yml")
def update_user_password():
    """function to update user password"""
    data = request.get_json()
    try:
        new_password = data['password']
        email = data['email']
    except KeyError:
        return jsonify({"message":"No username or password provided!"}), 400
    if re.match(r'[a-zA-Z0-9.-_]+@[a-z]+\.[a-z]+', email):
        if new_password.isalpha():
            response = jsonify({"message":"password can't be only alphabets"}), 400
        else:
            user_exit = Users.query.filter_by(email=email).first()
            if user_exit.password == new_password:
                response = jsonify({"message":"New password can't be the same as old password"}), 400
            else:
                if user_exit:
                    user_exit.password = new_password
                    user_exit.save()
                    response = jsonify({'message':"Password updated successfully!"}), 201
    else:
        response = jsonify({"message":"wrong email format!"}), 400
    return response

@app.route('/recipe/api/v1.0/user/view', methods=['GET'])
@token_required
@swag_from("/apps/docs/viewuser.yml")
def view_users(current_user):
    """function to view users list"""
    userlist = Users.getuser(current_user)
    if userlist:
        return jsonify({"User":userlist}), 200

@app.route('/recipe/api/v1.0/user/login', methods=['POST'])
@swag_from("/apps/docs/loginuser.yml")
def login_user():
    """function to login a user and get a token"""
    data = request.get_json()
    username = str(data['username']).strip()
    password = str(data['password']).strip()
    if not username or not password:
        return make_response('Invalid username or password', 400, \
                                {'WWW-Authentication' : 'Basic realm="Login required!'})
    user = Users.query.filter(Users.username == username, Users.password == password).first()
    if user:
        token = BlacklistTokens.generate_token(user.id)
        response = jsonify({'token': token.decode('UTF-8')}), 200
    else:
        response = jsonify({"message":"Invalid username or password"}), 400
    return response

@app.route('/recipe/api/v1.0/user/logout', methods=['POST'])
@token_required
@swag_from("/apps/docs/logoutuser.yml")
def logout(current_user):
    """function to logout users"""
    token = request.headers['x-access-token']
    blacklisted = BlacklistTokens.query.filter_by(token=token).first()
    if blacklisted:
        response = jsonify({"message": "Token already blacklisted. Please login again!"}), 401
    else:
        blacklisttoken = BlacklistTokens(token=token)
        if blacklisttoken:
            blacklisttoken.save()
            response = jsonify({"message": "Your loggout Successfully"}), 200
    return response

@app.route('/recipe/api/v1.0/user/delete', methods=['DELETE'])
@token_required
@swag_from("/apps/docs/deleteuser.yml")
def delete_user(current_user):
    """function to delete a user"""
    user = Users.query.filter_by(id=current_user.id).first()
    if user and user.id == current_user.id:
        user.delete()
        return jsonify({"message": "user {} was deleted successfully".\
                        format(current_user.username)}), 200

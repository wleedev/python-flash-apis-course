from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, \
    fresh_jwt_required, jwt_required, get_raw_jwt
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp

from blocklist import BLOCKLIST
from models.user import UserModel

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                          type=str,
                          required=True,
                          help="This field cannot be empty"
                          )
_user_parser.add_argument('password',
                          type=str,
                          required=True,
                          help="This field cannot be empty"
                          )


class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "User already exists."}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created successfully."}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User {} not found'.format(user_id)}, 404
        return user.json()

    @classmethod
    @fresh_jwt_required
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User {} not found'.format(user_id)}, 404
        user.delete_from_db()
        return {'message': 'User {} deleted'.format(user_id)}, 200

    def put(self, user_id):
        data = _user_parser.parse_args()

        try:
            user = UserModel.find_by_id(user_id)
        except:
            return {"message": "An error occurred whilst searching for the user"}, 500

        if user:
            user.password = data['password']
        else:
            user = UserModel(data['username'], data['password'])

        user.upsert()

        return user.json()


class UserList(Resource):
    def get(self):
        return {'users': [user.json() for user in UserModel.query.all()]}


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = _user_parser.parse_args()

        user = UserModel.find_by_username(data['username'])

        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                       'access_token': access_token,
                       'refresh_token': refresh_token
                   }, 200
        return {'message': 'Invalid credential'}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']  # jti is JWT ID, a unique identifier for a JWT
        BLOCKLIST.add(jti)
        return {'message': 'Successfully logged out.'}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200

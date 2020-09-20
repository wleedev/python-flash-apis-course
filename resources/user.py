from flask_restful import Resource, reqparse
from models.user import UserModel


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be empty"
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be empty"
                        )

    def post(self):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "User already exists."}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created successfully."}, 201


class User(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be empty"
                        )

    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User {} not found'.format(user_id)}, 404
        return user.json()


    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User {} not found'.format(user_id)}, 404
        user.delete_from_db()
        return {'message': 'User {} deleted'.format(user_id)}, 200

    def put(self, user_id):
        data = User.parser.parse_args()

        try:
            user = UserModel.find_by_id(user_id)
        except:
            return {"message": "An error occurred whilst searching for the user"}, 500

        if user:
            user.password = data['password']
        else:
            user = UserModel(user_id, data['username'], data['password'])

        user.upsert()

        return user.json()


class UserList(Resource):
    def get(self):
        return {'users': [user.json() for user in UserModel.query.all()]}

from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.store import StoreModel


class Store(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name',
                        type=str,
                        required=True,
                        help="Store name cannot be empty"
                        )

    @jwt_required()
    def get(self, name):
        try:
            store = StoreModel.find_by_name(name)
        except:
            return {"message": "An error occurred whilst looking up the store"}, 500

        if store:
            return store.json()
        return {'message': 'Store not found'}, 404

    def post(self, name):
        if StoreModel.find_by_name(name):
            return {'message': "A store with name '{}' already exists.".format(name)}, 400

        # data = Store.parser.parse_args()
        store = StoreModel(name)

        try:
            store.upsert()
        except:
            return {"message": "An error occurred whilst inserting the store"}, 500

        return store.json(), 201

    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
        else:
            return {'message': 'Store {} not found'.format(name)}, 404

        return {'message': "Store deleted"}


class StoreList(Resource):
    def get(self):
        return {'stores': [store.json() for store in StoreModel.query.all()]}
        # alternatively, {'stores': list(map(lambda x: x.json(), StoreModel.query.all()))}


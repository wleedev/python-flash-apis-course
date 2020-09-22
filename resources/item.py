from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims, jwt_optional, get_jwt_identity, fresh_jwt_required
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help="This field cannot be empty"
                        )
    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help="Store ID cannot be empty"
                        )

    @jwt_required
    def get(self, name):
        try:
            item = ItemModel.find_by_name(name)
        except:
            return {"message": "An error occurred whilst looking up the item"}, 500

        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400

        data = Item.parser.parse_args()
        item = ItemModel(name, data['price'], data['store_id'])

        try:
            item.upsert()
        except:
            return {"message": "An error occurred whilst inserting the item"}, 500

        return item.json(), 201

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required'
                    }, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        else:
            return {'message': 'Item {} not found'.format(name)}, 404

        return {'message': "Item deleted"}

    def put(self, name):
        data = Item.parser.parse_args()

        try:
            item = ItemModel.find_by_name(name)
        except:
            return {"message": "An error occurred whilst inserting the item"}, 500

        if item:
            item.price = data['price']
            item.store_id = data['store_id']
        else:
            item = ItemModel(name, data['price'], data['store_id'])

        item.upsert()

        return item.json()


class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]

        if user_id:
            return {'items': items}, 200
        return {
            'item': [item['name'] for item in items],
            'message': 'More data available if you log in'
        }, 200

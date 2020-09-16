import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help="This field cannot be empty"
                        )

    @jwt_required()
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
        item = ItemModel(name, data['price'])

        try:
            item.insert()
        except:
            return {"message": "An error occurred whilst inserting the item"}, 500

        return item.json(), 201

    def delete(self, name):
        if ItemModel.find_by_name(name):
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()

            query = "delete from items where name = ?"
            cursor.execute(query, (name,))

            connection.commit()
            connection.close()

            return {'message': 'Item deleted'}
        return {'message': 'Item does not exist'}, 404

    def put(self, name):
        data = Item.parser.parse_args()

        try:
            existing_item = ItemModel.find_by_name(name)
        except:
            return {"message": "An error occurred whilst inserting the item"}, 500

        updated_item = ItemModel(name, data['price'])

        if existing_item:
            try:
                updated_item.update()
            except:
                return {"message": "An error occurred whilst updating the item"}, 500
        else:
            try:
                updated_item.insert()
            except:
                return {"message": "An error occurred whilst inserting the item"}, 500

        return updated_item.json()


class ItemList(Resource):
    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "select * from items"
        result = cursor.execute(query)
        items = []
        for row in result:
            items.append({'name': row[0], 'price': row[1]})

        connection.close()
        return {'items': items}

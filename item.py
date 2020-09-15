import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from flask import jsonify


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
            item = self.find_by_name(name)
        except:
            return {"message": "An error occurred whilst inserting the item"}, 500

        if item:
            return item
        return {'message': 'Item not found'}, 404

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "select * from items where name = ?"
        result = cursor.execute(query, (name,))

        row = result.fetchone()
        connection.close()

        if row:
            return {'item': {'name': row[0], 'price': row[1]}}

    @classmethod
    def insert(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "insert into items values (?, ?)"
        cursor.execute(query, (item['name'], item['price']))

        connection.commit()
        connection.close()

    @classmethod
    def update(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "update items set price = ? where name = ?"
        cursor.execute(query, (item['price'], item['name']))

        connection.commit()
        connection.close()

        return {'message': 'Item updated'}

    def post(self, name):
        if self.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400

        data = Item.parser.parse_args()
        item = {'name': name, 'price': data['price']}

        try:
            self.insert(item)
        except:
            return {"message": "An error occurred whilst inserting the item"}, 500

        return item, 201

    def delete(self, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "delete from items where name = ?"
        cursor.execute(query, (name,))

        connection.commit()
        connection.close()

        return {'message': 'Item deleted'}

    def put(self, name):
        data = Item.parser.parse_args()

        try:
            existing_item = self.find_by_name(name)
        except:
            return {"message": "An error occurred whilst inserting the item"}, 500

        updated_item = {'name': name, 'price': data['price']}

        if existing_item:
            try:
                self.update(updated_item)
            except:
                return {"message": "An error occurred whilst updating the item"}, 500
        else:
            try:
                self.insert(updated_item)
            except:
                return {"message": "An error occurred whilst inserting the item"}, 500

        return updated_item


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

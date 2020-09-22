import unittest
import sqlite3
from flask import Flask
from app import db


class AppDBTests(unittest.TestCase):

    def setUp(self):
        """
        Creates a new database for the unit test to use
        """
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()
            self.populate_db()  # Your function that adds test data.

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        self.app = Flask(__name__)
        db.init_app(self.app)
        with self.app.app_context():
            db.drop_all()

    def populate_db(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        create_table = "create table if not exists users (id integer primary key, username text, password text)"
        cursor.execute(create_table)
        cursor.execute("delete from users")
        cursor.execute("insert into users values (1, 'user1', 'abc')")

        create_table = "create table if not exists items (id integer primary key, name text, price real, store_id)"
        cursor.execute(create_table)
        cursor.execute("delete from items")
        cursor.execute("insert into items values (1, 'item1', 10.99, 1)")

        create_table = "create table if not exists stores (id integer primary key, name text, items text)"
        cursor.execute(create_table)
        cursor.execute("delete from stores")
        cursor.execute("insert into stores values (1, 'store1', 'item1')")

        connection.commit()
        connection.close()

    def test_something(self):
        pass


if __name__ == '__main__':
    unittest.main()

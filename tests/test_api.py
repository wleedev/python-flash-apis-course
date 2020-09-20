import requests
import sqlite3
import unittest


class TestAPI(unittest.TestCase):
    API_BASE_URL = 'http://127.0.0.1:5000'
    HEALTH_URL = '{}/health'.format(API_BASE_URL)

    # Users URLs
    ALL_USERS_URL = '{}/users'.format(API_BASE_URL)
    REGISTER_URL = '{}/register'.format(API_BASE_URL)
    AUTHORISE_URL = '{}/auth'.format(API_BASE_URL)
    USER_URL = '{}/user/'.format(API_BASE_URL)

    # Items URLs
    ALL_ITEMS_URL = '{}/items'.format(API_BASE_URL)
    ITEM_URL = '{}/item/'.format(API_BASE_URL)

    # Stores URLs
    ALL_STORES_URL = '{}/stores'.format(API_BASE_URL)
    STORE_URL = '{}/store/'.format(API_BASE_URL)

    OK_OBJ = {"message": "ok"}

    # Delete any records in DB
    connection = sqlite3.connect('../data.db')
    cursor = connection.cursor()

    cursor.execute("delete from users")
    cursor.execute("delete from items")
    cursor.execute("delete from stores")

    connection.commit()
    connection.close()

    def setUp(self):
        pass

    def test_010_health(self):
        """Check health endpoint available"""
        r = requests.get(self.HEALTH_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual((r.json()), self.OK_OBJ)

    def test_020_empty_items(self):
        """Check no items in DB via endpoint"""
        r = requests.get(self.ALL_ITEMS_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"items": []})

    def test_030_empty_items(self):
        """Check no users in DB via endpoint"""
        r = requests.get(self.ALL_USERS_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"users": []})

    def test_040_empty_items(self):
        """Check no stores in DB via endpoint"""
        r = requests.get(self.ALL_STORES_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"stores": []})

    def test_050_register_user1(self):
        """Register new user1"""
        r = requests.post(self.REGISTER_URL, {"username": "user1", "password": "abc"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json(), {"message": "User created successfully."})

    def test_060_register_user2(self):
        """Register new user2"""
        r = requests.post(self.REGISTER_URL, {"username": "user2", "password": "xyz"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json(), {"message": "User created successfully."})

    def test_070_authorise_user1(self):
        """Authorise user1"""
        r = requests.post(self.AUTHORISE_URL, json={"username": "user1", "password": "abc"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['Content-Length'], '193')

    def test_080_create_store1(self):
        """Create a new store1"""
        r = requests.post(self.STORE_URL + 'store1')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['name'], 'store1')

    def test_090_create_store(self):
        """Create a new store2"""
        r = requests.post(self.STORE_URL + 'store2')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['name'], 'store2')

    def test_100_create_item1(self):
        """Create a new item at store1"""
        r = requests.post(self.ITEM_URL + 'item1', json={"price": 9.99, "store_id": 1})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['name'], 'item1')
        self.assertEqual(r.json()['price'], 9.99)
        self.assertEqual(r.json()['store_id'], 1)

    def test_110_create_item2(self):
        """Create a new item at store2"""
        r = requests.post(self.ITEM_URL + 'item2', json={"price": 29.99, "store_id": 2})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['name'], 'item2')
        self.assertEqual(r.json()['price'], 29.99)
        self.assertEqual(r.json()['store_id'], 2)

    def test_120_get_item1(self):
        """Get the item just created, item1, with JWT"""
        r = requests.post(self.AUTHORISE_URL, json={"username": "user1", "password": "abc"})
        access_token = r.json()['access_token']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['Content-Length'], '193')

        headers = {'Authorization': 'JWT {}'.format(access_token)}
        r = requests.get(self.ITEM_URL + 'item1', headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['name'], 'item1')
        self.assertEqual(r.json()['price'], 9.99)
        self.assertEqual(r.json()['store_id'], 1)

    def test_130_get_store1(self):
        """Get store1 with JWT"""
        r = requests.post(self.AUTHORISE_URL, json={"username": "user1", "password": "abc"})
        access_token = r.json()['access_token']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['Content-Length'], '193')

        headers = {'Authorization': 'JWT {}'.format(access_token)}
        r = requests.get(self.STORE_URL + 'store1', headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {
            "id": 1,
            "name": "store1",
            "items": [
                {
                    "id": 1,
                    "name": "item1",
                    "price": 9.99,
                    "store_id": 1
                }
            ]
        })

    def test_140_get_user1(self):
        """Get user1 with JWT"""
        r = requests.post(self.AUTHORISE_URL, json={"username": "user1", "password": "abc"})
        access_token = r.json()['access_token']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['Content-Length'], '193')

        headers = {'Authorization': 'JWT {}'.format(access_token)}
        r = requests.get(self.USER_URL + '1', headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {
            "id": 1,
            "username": "user1"
        })

    def test_150_get_all_items(self):
        """Get all items"""
        r = requests.get(self.ALL_ITEMS_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"items": [
            {'id': 1, 'name': 'item1', 'price': 9.99, 'store_id': 1},
            {'id': 2, 'name': 'item2', 'price': 29.99, 'store_id': 2}]
        })

    def test_160_get_all_stores(self):
        """Get all stores"""
        r = requests.get(self.ALL_STORES_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {
            "stores": [
                {
                    "id": 1,
                    "name": "store1",
                    "items": [
                        {
                            "id": 1,
                            "name": "item1",
                            "price": 9.99,
                            "store_id": 1
                        }
                    ]
                },
                {
                    "id": 2,
                    "name": "store2",
                    "items": [
                        {
                            "id": 2,
                            "name": "item2",
                            "price": 29.99,
                            "store_id": 2
                        }
                    ]
                }
            ]
        }
                         )

    def test_170_get_all_user(self):
        """Get all users"""
        r = requests.get(self.ALL_USERS_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {
            "users": [
                {
                    "id": 1,
                    "username": "user1"
                },
                {
                    "id": 2,
                    "username": "user2"
                }
            ]
        })

    def test_180_update_item1(self):
        """Update item1 price"""
        r = requests.put(self.ITEM_URL + 'item1', json={
            "price": 13.99,
            "store_id": 1
        })
        self.assertEqual(r.status_code, 200)

    def test_190_update_user1(self):
        """Update user1 password"""
        r = requests.get(self.USER_URL + '1', json={"password": "qrs"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {
            "id": 1,
            "username": "user1"
        })

    def test_200_delete_item1(self):
        """Delete item1"""
        r = requests.delete(self.ITEM_URL + 'item1')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"message": "Item deleted"})

        # Confirm item1 has been deleted
        r = requests.post(self.AUTHORISE_URL, json={"username": "user1", "password": "abc"})
        access_token = r.json()['access_token']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['Content-Length'], '193')

        headers = {'Authorization': 'JWT {}'.format(access_token)}
        r = requests.get(self.ITEM_URL + 'item1', headers=headers)
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json(), {"message": "Item not found"})

    def test_210_delete_store1(self):
        """Delete store1"""
        r = requests.delete(self.STORE_URL + 'store1')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"message": "Store deleted"})

        # Confirm store1 has been deleted
        r = requests.post(self.AUTHORISE_URL, json={"username": "user1", "password": "abc"})
        access_token = r.json()['access_token']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['Content-Length'], '193')

        headers = {'Authorization': 'JWT {}'.format(access_token)}
        r = requests.get(self.STORE_URL + 'store1', headers=headers)
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json(), {"message": "Store not found"})

    def test_220_delete_user2(self):
        """Delete user2"""
        r = requests.delete(self.USER_URL + '2')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"message": "User 2 deleted"})

        # Confirm user2 has been deleted
        r = requests.get(self.USER_URL + '2')
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json(), {"message": "User 2 not found"})

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()

import requests
import sqlite3
import unittest


class TestAPI(unittest.TestCase):
    API_BASE_URL = 'http://127.0.0.1:5000'
    HEALTH_URL = f'{API_BASE_URL}/health'
    AUTH_TOKEN_TYPE = 'Bearer'
    AUTH_HEADER_CONTENT_LENGTH = '612'

    # Users URLs
    ALL_USERS_URL = f'{API_BASE_URL}/users'
    REGISTER_URL = f'{API_BASE_URL}/register'
    AUTHORISE_URL = f'{API_BASE_URL}/login'
    LOGOUT_URL = f'{API_BASE_URL}/logout'
    USER_URL = f'{API_BASE_URL}/user/'
    REFRESH_URL = f'{API_BASE_URL}/refresh'

    # Items URLs
    ALL_ITEMS_URL = f'{API_BASE_URL}/items'
    ITEM_URL = f'{API_BASE_URL}/item/'

    # Stores URLs
    ALL_STORES_URL = f'{API_BASE_URL}/stores'
    STORE_URL = f'{API_BASE_URL}/store/'

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
        self.assertEqual((r.json()), {"message": "ok"})

    def test_020_empty_items(self):
        """Check no items in DB via SQL"""
        connection = sqlite3.connect('../data.db')
        cursor = connection.cursor()

        cursor.execute("select count(*) from items")
        result = cursor.fetchone()

        connection.commit()
        connection.close()

        self.assertEqual(result[0], 0)

    def test_030_empty_users(self):
        """Check no users in DB via endpoint"""
        r = requests.get(self.ALL_USERS_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"users": []})

    def test_040_empty_stores(self):
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
        self.assertEqual(r.headers['Content-Length'], self.AUTH_HEADER_CONTENT_LENGTH)

    def test_080_create_store1(self):
        """Create a new store1"""
        r = requests.post(self.STORE_URL + 'store1')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['name'], 'store1')

    def test_090_create_store2(self):
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
        self.assertEqual(r.headers['Content-Length'], self.AUTH_HEADER_CONTENT_LENGTH)

        headers = {'Authorization': f'{self.AUTH_TOKEN_TYPE} {access_token}'}
        r = requests.get(self.ITEM_URL + 'item1', headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['name'], 'item1')
        self.assertEqual(r.json()['price'], 9.99)
        self.assertEqual(r.json()['store_id'], 1)

    def test_130_get_store1(self):
        """Get store1"""
        r = requests.get(self.STORE_URL + 'store1')
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
        self.assertEqual(r.headers['Content-Length'], self.AUTH_HEADER_CONTENT_LENGTH)

        headers = {'Authorization': f'{self.AUTH_TOKEN_TYPE} {access_token}'}
        r = requests.get(self.USER_URL + '1', headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {
            "id": 1,
            "username": "user1"
        })

    def test_150_get_all_items_not_logged_in(self):
        """Get all items when not logged in"""
        r = requests.get(self.ALL_ITEMS_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {'item': ['item1', 'item2'], 'message': 'More data available if you log in'})

    def test_155_get_all_items_logged_in(self):
        """Get all items whilst logged in"""
        r = requests.post(self.AUTHORISE_URL, json={"username": "user1", "password": "abc"})
        access_token = r.json()['access_token']
        headers = {'Authorization': f'{self.AUTH_TOKEN_TYPE} {access_token}'}
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['Content-Length'], self.AUTH_HEADER_CONTENT_LENGTH)

        r = requests.get(self.ALL_ITEMS_URL, headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {'items': [{'id': 1, 'name': 'item1', 'price': 9.99, 'store_id': 1},
                                              {'id': 2, 'name': 'item2', 'price': 29.99, 'store_id': 2}]})

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

    def test_200_delete_item1_non_admin(self):
        """Delete item1"""
        r = requests.post(self.AUTHORISE_URL, json={"username": "user2", "password": "xyz"})
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(r.json()['access_token'])
        self.assertIsNotNone(r.json()['refresh_token'])

        access_token = r.json()['access_token']
        headers = {'Authorization': f'{self.AUTH_TOKEN_TYPE} {access_token}'}

        r = requests.delete(self.ITEM_URL + 'item1', headers=headers)
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.json(), {"message": "Admin privilege required"})

        # Confirm item1 has not been deleted
        r = requests.get(self.ITEM_URL + 'item1', headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"id": 1, "name": "item1", "price": 13.99, "store_id": 1})

    # @unittest.skip
    def test_210_delete_item1_admin(self):
        """Delete item1"""
        r = requests.post(self.AUTHORISE_URL, json={"username": "user1", "password": "abc"})
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(r.json()['access_token'])
        self.assertIsNotNone(r.json()['refresh_token'])

        access_token = r.json()['access_token']
        headers = {'Authorization': f'{self.AUTH_TOKEN_TYPE} {access_token}'}

        r = requests.delete(self.ITEM_URL + 'item1', headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"message": "Item deleted"})

        # Confirm item1 has been deleted
        r = requests.get(self.ITEM_URL + 'item1', headers=headers)
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json(), {"message": "Item not found"})

    def test_210_delete_store1(self):
        """Delete store1"""
        r = requests.delete(self.STORE_URL + 'store1')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"message": "Store deleted"})

        # Confirm store1 has been deleted
        r = requests.get(self.STORE_URL + 'store1')
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json(), {"message": "Store not found"})

    def test_220_delete_user2_stale_access_token(self):
        """Delete user2 with not-fresh access token"""
        # Get refresh token
        r1 = requests.post(self.AUTHORISE_URL, json={"username": "user1", "password": "abc"})
        self.assertEqual(r1.status_code, 200)
        self.assertIsNotNone(r1.json()['access_token'])
        self.assertIsNotNone(r1.json()['refresh_token'])
        refresh_token = r1.json()['refresh_token']

        # Get non-fresh access token
        headers = {'Authorization': f'{self.AUTH_TOKEN_TYPE} {refresh_token}'}
        r2 = requests.post(self.REFRESH_URL, headers=headers)
        self.assertIsNotNone(r2.json()['access_token'])
        nonfresh_access_token = r2.json()['access_token']

        # Attempt to delete user2 with non-fresh access token
        headers = {'Authorization': f'{self.AUTH_TOKEN_TYPE} {nonfresh_access_token}'}
        r = requests.delete(f'{self.USER_URL}2', headers=headers)
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.json(), {
            'description': 'The supplied token is not fresh.',
            'error': 'fresh_token_required'
        })

        # Confirm user2 has not been deleted
        r = requests.post(self.AUTHORISE_URL, json={"username": "user1", "password": "abc"})
        access_token = r.json()['access_token']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['Content-Length'], self.AUTH_HEADER_CONTENT_LENGTH)

        # headers = {'Authorization': f'{self.AUTH_TOKEN_TYPE} {access_token}'}
        r = requests.get(self.USER_URL + '2', headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {
            "id": 2,
            "username": "user2"
        })

    def test_225_delete_user2_fresh_access_token(self):
        """Delete user2 with fresh access token"""
        r = requests.post(self.AUTHORISE_URL, json={"username": "user1", "password": "abc"})
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(r.json()['access_token'])
        self.assertIsNotNone(r.json()['refresh_token'])

        access_token = r.json()['access_token']
        headers = {'Authorization': f'{self.AUTH_TOKEN_TYPE} {access_token}'}
        r = requests.delete(f'{self.USER_URL}2', headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"message": "User 2 deleted"})

        # Confirm user2 has been deleted
        r = requests.get(f'{self.USER_URL}2')
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json(), {"message": "User 2 not found"})

    def test_230_update_non_existent_user9(self):
        """Update a user which doesn't already exist"""
        r = requests.put(self.USER_URL + '9', json={"username": "user9", "password": "xxx"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {
            "id": 2,
            "username": "user9"
        })

    def test_240_update_non_existent_item9(self):
        """Update an item which doesn't already exist"""
        r = requests.put(self.ITEM_URL + 'item9', json={
            "price": 99.99,
            "store_id": 1
        })
        self.assertEqual(r.status_code, 200)

    @unittest.skip
    def test_250_get_item2_as_blocklist_user4(self):
        """Fail to the item2, as blocked user4"""
        r = requests.post(self.REGISTER_URL, {"username": "user3", "password": "def"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json(), {"message": "User created successfully."})

        r = requests.post(self.REGISTER_URL, {"username": "user4", "password": "ghi"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json(), {"message": "User created successfully."})

        r = requests.post(self.AUTHORISE_URL, json={"username": "user4", "password": "ghi"})
        access_token = r.json()['access_token']
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.headers['Content-Length'], 614)

        headers = {'Authorization': f'{self.AUTH_TOKEN_TYPE} {access_token}'}
        r = requests.get(self.ITEM_URL + 'item2', headers=headers)
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.json(), {
            "description": "The supplied token has been revoked.",
            "error": "token_revoked"
        })

    def test_260_logout_user1(self):
        """Log in, get item1, log out"""
        r = requests.post(self.AUTHORISE_URL, json={"username": "user1", "password": "abc"})
        access_token = r.json()['access_token']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['Content-Length'], self.AUTH_HEADER_CONTENT_LENGTH)

        headers = {'Authorization': f'{self.AUTH_TOKEN_TYPE} {access_token}'}
        r = requests.get(self.ITEM_URL + 'item2', headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['name'], 'item2')
        self.assertEqual(r.json()['price'], 29.99)
        self.assertEqual(r.json()['store_id'], 2)

        # Log out
        r = requests.post(self.LOGOUT_URL, headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"message": "Successfully logged out."})

        r = requests.get(self.ITEM_URL + 'item2', headers=headers)
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.json(), {
            "description": "The supplied token has been revoked.",
            "error": "token_revoked"
        })

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()

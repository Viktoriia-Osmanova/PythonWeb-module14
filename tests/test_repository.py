import unittest
from repository.repository import UserRepository

class TestUserRepository(unittest.TestCase):
    def setUp(self):
        self.user_repo = UserRepository()

    def test_add_user(self):
        user_data = {"username": "test_user", "password": "test_password"}
        user_id = self.user_repo.add_user(user_data)
        self.assertIsNotNone(user_id)

    def test_get_user_by_username(self):
        user_data = {"username": "test_user", "password": "test_password"}
        self.user_repo.add_user(user_data)
        user = self.user_repo.get_user_by_username("test_user")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "test_user")

    def test_get_user_by_username_nonexistent(self):
        user = self.user_repo.get_user_by_username("nonexistent_user")
        self.assertIsNone(user)

    def test_delete_user(self):
        user_data = {"username": "test_user", "password": "test_password"}
        self.user_repo.add_user(user_data)
        deleted = self.user_repo.delete_user("test_user")
        self.assertTrue(deleted)

if __name__ == "__main__":
    unittest.main()

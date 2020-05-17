import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
from cool_app import ServiceLogger
from cool_app.persistence.user_profiles import User
from cool_app.persistence import engine
from tests import DummyLogger


class TestEngineInit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with engine.connect() as connection:
            connection.execute('DELETE FROM notes')
            connection.execute('DELETE FROM user_profiles')
            

    def test_engine_init_user(self):
        u = User(logger=DummyLogger())
        self.assertIsNotNone(u)
        self.assertIsNotNone(u.engine)

    def test_engine_create_user(self):
        u = User(logger=DummyLogger())
        self.assertIsNotNone(u)
        self.assertIsNotNone(u.engine)
        u.user_alias = 'TestUser'
        u.user_email_address = 'testuser@example.tld'
        u.account_status = 1
        result = u.create_user_profile()
        self.assertTrue(result)
        self.assertIsInstance(u.uid, int)

    def test_load_user_profile_by_email_address_basic(self):
        u = User(logger=DummyLogger())
        u.user_alias = 'user2'
        u.user_email_address = 'user2@example.tld'
        u.account_status = 1
        u.create_user_profile()
        u = User(logger=DummyLogger())
        u.user_alias = 'user3'
        u.user_email_address = 'user3@example.tld'
        u.account_status = 0
        u.create_user_profile()
        u = None
        test_u = User(logger=DummyLogger())
        test_u.load_user_profile_by_email_address(user_email_address='user3@example.tld')
        self.assertIsNotNone(test_u.uid)
        self.assertIsInstance(test_u.uid, int)
        self.assertEqual(test_u.user_alias, 'user3')
        self.assertEqual(test_u.user_email_address, 'user3@example.tld')
        self.assertEqual(test_u.account_status, 0)
        test_u = User(logger=DummyLogger())
        test_u.load_user_profile_by_email_address(user_email_address='user2@example.tld')
        self.assertIsNotNone(test_u.uid)
        self.assertIsInstance(test_u.uid, int)
        self.assertEqual(test_u.user_alias, 'user2')
        self.assertEqual(test_u.user_email_address, 'user2@example.tld')
        self.assertEqual(test_u.account_status, 1)

    def test_load_user_profile_by_uid_user4(self):
        u1 = User(logger=DummyLogger())
        u1.user_alias = 'user4'
        u1.user_email_address = 'user4@example.tld'
        u1.account_status = 1
        u1.create_user_profile()
        uid = u1.uid
        test_u = User(logger=DummyLogger())
        test_u.load_user_profile_by_uid(uid=uid)
        self.assertEqual(test_u.user_alias, 'user4')
        self.assertEqual(test_u.user_email_address, 'user4@example.tld')
        self.assertEqual(test_u.account_status, 1)

    def test_update_user_profile_user5(self):
        u = User(logger=DummyLogger())
        u.user_alias = 'user5'
        u.user_email_address = 'user5@example.tld'
        u.account_status = 1
        u.create_user_profile()
        u.account_status = 0
        result = u.update_user_profile()
        uid = u.uid
        self.assertTrue(result)
        test_u = User(logger=DummyLogger())
        test_u.load_user_profile_by_uid(uid=uid)
        self.assertEqual(test_u.account_status, 0)

# EOF

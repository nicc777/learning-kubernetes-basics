import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
from cool_app import ServiceLogger
from cool_app.persistence.notes import Note, Notes
from cool_app.persistence.user_profiles import User
from cool_app.service_app import generate_generic_error_response
from cool_app.persistence import engine
from tests import DummyLogger


L = DummyLogger()

class TestServiceApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with engine.connect() as connection:
            connection.execute('DELETE FROM notes')
            connection.execute('DELETE FROM user_profiles')
        for uid in range(1, 5):
            u = User(logger=L)
            u.user_alias = 'user{}'.format(uid)
            u.user_email_address = 'user{}@example.tld'.format(uid)
            u.account_status = 1
            u.create_user_profile()
            for nid in range(1, 5):
                n = Note(logger=L)
                n.note_timestamp = int('1{}1{}0'.format(u.uid, nid))
                n.note_text = 'Note nr {} for user {}'.format(nid, u.uid)
                n.uid = u.uid
                n.create_note()

    def test_generate_generic_error_response(self):
        error_code = 123
        error_msg = 'TEST MESSAGES'
        result = generate_generic_error_response(error_code=error_code, error_message=error_msg)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertTrue('ErrorCode' in result)
        self.assertTrue('ErrorMessage' in result)
        self.assertEqual(result['ErrorCode'], error_code)
        self.assertEqual(result['ErrorMessage'], error_msg)

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
from cool_app import ServiceLogger
from cool_app.persistence import engine, test_data_source
from tests import DummyLogger


class TestEngineInit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with engine.connect() as connection:
            connection.execute('DELETE FROM notes')
            connection.execute('DELETE FROM user_profiles')
            connection.execute('INSERT INTO user_profiles ( user_alias, user_email_address, account_status ) VALUES ( \'user1\', \'user1@example.tld\', 0 )')

    def test_engine_init_bare(self):
        self.assertIsNotNone(engine)

    def test_engine_basic_test(self):
        L=DummyLogger()
        self.assertTrue(test_data_source(L=L))
        self.assertEqual(len(L.log_lines), 1)


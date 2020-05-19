import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import unittest
from cool_app import ServiceLogger
from cool_app.persistence import engine, test_data_source, db_create_user_profile, db_load_user_profile_by_email_address
from tests import DummyLogger
import time
import traceback


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


class MockResultSet:

    def __init__(self, expected_result):
        self.expected_result = expected_result

    def fetchone(self):
        return self.expected_result


class MockConnection:

    def __init__(self, expected_result):
        self.expected_result = expected_result
        self.execute_called = False

    def execute(self, *args, **kwargs):
        self.execute_called = True
        if isinstance(self.expected_result, Exception):
            raise self.expected_result
        return self.expected_result

    def fetchone(self, *args, **kwargs):
        return self.expected_result

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        pass


class MockEngine:

    def __init__(self, connection=MockConnection(expected_result=None)):
        self.connection = connection

    def connect(self, *args, **kwargs):
        return self.connection


class TestDbIntergation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with engine.connect() as connection:
            connection.execute('DELETE FROM notes')
            connection.execute('DELETE FROM user_profiles')

    def test_db_create_user_profile(self):
        result = db_create_user_profile(
            user_alias='user1',
            user_email_address='user1@example.tld',
            account_status=1,
            L=DummyLogger()
        )
        self.assertTrue(result)

    def test_db_load_user_profile_by_email_address(self):
        self.assertTrue(
            db_create_user_profile(
                user_alias='user2',
                user_email_address='user2@example.tld',
                account_status=1,
                L=DummyLogger()
            )
        )
        result = db_load_user_profile_by_email_address(user_email_address='user2@example.tld', L=DummyLogger())
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertTrue('uid' in result)
        self.assertIsInstance(result['uid'], int)
        self.assertTrue(result['uid'] > 0)


class TestCircuitBreakerWithMocking(unittest.TestCase):

    def test_db_create_user_profile(self):
        L = DummyLogger()
        runs = {
            '1': {
                'Engine': MockEngine(connection=MockConnection(expected_result=True)),
                'ExpectException': False,
                'Result': True,
                'Sleep': 2
            },
            '2': {
                'Engine': MockEngine(connection=MockConnection(expected_result=Exception('Broken'))),
                'ExpectException': True,
                'Result': None,
                'Sleep': 2
            },
            '3': {
                'Engine': MockEngine(connection=MockConnection(expected_result=Exception('Broken'))),
                'ExpectException': True,
                'Result': None,
                'Sleep': 35
            },
            '4': {
                'Engine': MockEngine(connection=MockConnection(expected_result=True)),
                'ExpectException': False,
                'Result': True,
                'Sleep': 2
            }
        }
        keys = list(runs.keys())
        keys.sort()
        for key in keys:
            exception_raised = False
            try:
                result = db_create_user_profile(user_alias='user01', user_email_address='user01@example.tld', account_status=1, f_engine=runs[key]['Engine'], L=L)
                self.assertEqual(result, runs[key]['Result'], 'Result test failed for Run # {}'.format(key))
            except:
                L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
                exception_raised = True
            self.assertEqual(exception_raised, runs[key]['ExpectException'], 'Failed Exception. Run # {}'.format(key))
            if key == '3':
                self.assertFalse(runs[key]['Engine'].connection.execute_called, 'Run # {} circuit breaker failed. Call to back end was still made.'.format(key))
            else:
                self.assertTrue(runs[key]['Engine'].connection.execute_called, 'Run # {} circuit breaker failed. Call to back end was NOT made.'.format(key))
            print('patience... sleeping for {} seconds'.format(runs[key]['Sleep']))
            time.sleep(runs[key]['Sleep'])

    def test_db_load_user_profile_by_email_address(self):
        L = DummyLogger()
        profile_data = dict()
        profile_data['uid'] = 101
        profile_data['user_alias'] = 'SomeUser'
        profile_data['user_email_address'] = 'someuser@example.tld'
        profile_data['account_status'] = 0
        runs = {
            '1': {
                'Engine': MockEngine(connection=MockConnection(expected_result=MockResultSet(expected_result=profile_data))),
                'ExpectException': False,
                'Result': profile_data,
                'Sleep': 2
            },
            '2': {
                'Engine': MockEngine(connection=MockConnection(expected_result=Exception('Broken'))),
                'ExpectException': True,
                'Result': None,
                'Sleep': 2
            },
            '3': {
                'Engine': MockEngine(connection=MockConnection(expected_result=Exception('Broken'))),
                'ExpectException': True,
                'Result': None,
                'Sleep': 35
            },
            '4': {
                'Engine': MockEngine(connection=MockConnection(expected_result=MockResultSet(expected_result=profile_data))),
                'ExpectException': False,
                'Result': profile_data,
                'Sleep': 1
            }
        }
        keys = list(runs.keys())
        keys.sort()
        for key in keys:
            exception_raised = False
            try:
                result = db_load_user_profile_by_email_address(user_email_address='someuser@example.tld', f_engine=runs[key]['Engine'], L=L)
                self.assertIsNotNone(result, 'Run # {} returned None. Expected a dict.'.format(key))
                self.assertIsInstance(result, dict, 'Run # {} did not return an expected dict. Return type: {}'.format(key, type(result)))
                self.assertTrue('uid' in result)
                self.assertTrue('user_alias' in result)
                self.assertTrue('user_email_address' in result)
                self.assertTrue('account_status' in result)
            except:
                L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
                exception_raised = True
            self.assertEqual(exception_raised, runs[key]['ExpectException'], 'Failed Exception. Run # {}'.format(key))
            if key == '3':
                self.assertFalse(runs[key]['Engine'].connection.execute_called, 'Run # {} circuit breaker failed. Call to back end was still made.'.format(key))
            else:
                self.assertTrue(runs[key]['Engine'].connection.execute_called, 'Run # {} circuit breaker failed. Call to back end was NOT made.'.format(key))
            print('patience... sleeping for {} seconds'.format(runs[key]['Sleep']))
            time.sleep(runs[key]['Sleep'])
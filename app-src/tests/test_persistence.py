import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import unittest
from cool_app import ServiceLogger
from cool_app.persistence import engine, test_data_source, db_create_user_profile, db_load_user_profile_by_email_address, db_load_user_profile_by_uid, db_update_user_profile, db_create_note, db_load_note
from tests import DummyLogger
import time
import traceback
from sqlalchemy.sql import text


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

    def test_db_load_user_profile_by_uid(self):
        self.assertTrue(
            db_create_user_profile(
                user_alias='user3',
                user_email_address='user3@example.tld',
                account_status=1,
                L=DummyLogger()
            )
        )
        uid = db_load_user_profile_by_email_address(user_email_address='user3@example.tld', L=DummyLogger())['uid']
        result = db_load_user_profile_by_uid(uid=uid, L=DummyLogger())
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['user_email_address'], 'user3@example.tld')

    def test_db_update_user_profile(self):
        self.assertTrue(
            db_create_user_profile(
                user_alias='user4',
                user_email_address='user4@example.tld',
                account_status=1,
                L=DummyLogger()
            )
        )
        uid = db_load_user_profile_by_email_address(user_email_address='user4@example.tld', L=DummyLogger())['uid']
        update_result = db_update_user_profile(user_alias='user04', user_email_address='user04@example2.tld', uid=uid, account_status=1, L=DummyLogger())
        self.assertTrue(update_result)
        profile = db_load_user_profile_by_uid(uid=uid, L=DummyLogger())
        self.assertIsNotNone(profile)
        self.assertIsInstance(profile, dict)
        self.assertTrue('user_email_address' in profile)
        self.assertEqual(profile['user_email_address'], 'user04@example2.tld')


class TestDbIntergationForNote(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with engine.connect() as connection:
            connection.execute('DELETE FROM notes')
            connection.execute('DELETE FROM user_profiles')
            for uid in range(1, 5):
                user_alias = 'user{}'.format(uid)
                user_email_address = 'user{}@example.tld'.format(uid)
                account_status = 1
                connection.execute(text('INSERT INTO user_profiles ( user_alias, user_email_address, account_status ) VALUES ( :f1, :f2, :f3 )'), f1=user_alias, f2=user_email_address, f3=account_status)

    def setUp(self):
        self.uids = list()
        with engine.connect() as connection:
            for row in connection.execute('SELECT uid FROM user_profiles'):
                self.uids.append(row[0])
        self.uids.sort()

    def test_db_create_note(self):
        if len(self.uids) <= 0:
            self.fail('No UIDs available')
        L = DummyLogger()
        result = db_create_note(uid=self.uids[0], note_timestamp='1001', note_text='Test note.', L=L)
        self.assertTrue(result)

    def test_db_load_note(self):
        if len(self.uids) <= 0:
            self.fail('No UIDs available')
        L = DummyLogger()
        db_create_note(uid=self.uids[0], note_timestamp='1002', note_text='Test note.', L=L)
        result = db_load_note(uid=self.uids[0], note_timestamp='1002', L=L)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertTrue('uid' in result)
        self.assertTrue('note_timestamp' in result)
        self.assertTrue('note_text' in result)
        self.assertEqual(result['note_text'], 'Test note.')


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

    def test_db_load_user_profile_by_uid(self):
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
                result = db_load_user_profile_by_uid(uid=101, f_engine=runs[key]['Engine'], L=L)
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
    
    def test_db_update_user_profile(self):
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
                result = db_update_user_profile(user_alias='user01', user_email_address='user01@example.tld', uid=101, account_status=1, f_engine=runs[key]['Engine'], L=L)
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
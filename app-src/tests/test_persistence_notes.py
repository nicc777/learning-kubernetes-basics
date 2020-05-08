'''
    IMPORTANT NOTE
    --------------

    If you run these tests a great many times, you may run into a situation where the INT values for "uid" etc. become 
    too large. If you start to run into integer size related issues (i.e. "psycopg2.errors.NumericValueOutOfRange"),
    you may need to re-create the tables from scratch (DROP TABLE... CREATE TABLE).
'''
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
from cool_app.persistence import engine
from tests import DummyLogger


L = DummyLogger()

class TestNote(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with engine.connect() as connection:
            connection.execute('DELETE FROM notes')
            connection.execute('DELETE FROM user_profiles')
        for uid in range(1, 10):
            u = User(logger=L)
            u.user_alias = 'user{}'.format(uid)
            u.user_email_address = 'user{}@example.tld'.format(uid)
            u.account_status = 1
            u.create_user_profile()

    def setUp(self):
        self.uids = list()
        with engine.connect() as connection:
            for row in connection.execute('SELECT uid FROM user_profiles'):
                self.uids.append(row[0])


    def test_engine_init_note(self):
        n = Note(logger=L)
        self.assertIsNotNone(n)
        self.assertIsNotNone(n.engine)

    def test_create_note(self):
        n = Note(logger=L)
        n.note_timestamp = 1234567800
        n.uid = self.uids[0]
        n.note_text = 'Note nr 1'
        result = n.create_note()
        self.assertTrue(result)

    def test_load_note(self):
        n = Note(logger=L)
        n.note_timestamp = 1234567801
        n.uid = self.uids[1]
        n.note_text = 'Note nr 1'
        n.create_note()
        test_n = Note(logger=L)
        test_n.uid = self.uids[1]
        result = test_n.load_note(note_timestamp=1234567801)
        self.assertTrue(result)
        self.assertEqual(test_n.note_timestamp, n.note_timestamp)
        self.assertEqual(test_n.note_text, n.note_text)

    def test_update_note(self):
        n = Note(logger=L)
        n.note_timestamp = 1234567802
        n.uid = self.uids[2]
        n.note_text = 'Note nr 1'
        n.create_note()
        new_text = 'Note nr 1 - updated'
        n.update_note(updated_text=new_text)
        test_n = Note(logger=L)
        test_n.uid = self.uids[2]
        test_n.load_note(note_timestamp=1234567802)
        self.assertEqual(test_n.note_text, new_text)

    def test_delete_note(self):
        n = Note(logger=L)
        n.note_timestamp = 1234567803
        n.uid = self.uids[3]
        n.note_text = 'Note nr 1'
        n.create_note()
        n.delete_note()
        test_n = Note(logger=L)
        test_n.uid = self.uids[3]
        result = test_n.load_note(note_timestamp=1234567803)
        self.assertFalse(result)


class TestNotes(unittest.TestCase):

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

    def setUp(self):
        self.uids = list()
        with engine.connect() as connection:
            for row in connection.execute('SELECT uid FROM user_profiles'):
                self.uids.append(row[0])


    def test_engine_init_notes(self):
        n = Notes(logger=L)
        self.assertIsNotNone(n)
        self.assertIsNotNone(n.engine)

    def test_load_notes_(self):
        n = Notes(logger=L)
        uid = self.uids[0]
        n.uid = uid
        # int('1{}1{}0'.format(u.uid, nid))
        timestamp = int('1{}110'.format(uid))
        (notes_loaded, total_notes) = n.load_notes(start_timestamp=timestamp, limit=3)
        self.assertIsNotNone(notes_loaded)
        self.assertIsNotNone(total_notes)
        self.assertIsInstance(notes_loaded, int)
        self.assertIsInstance(total_notes, int)
        self.assertEqual(notes_loaded, 3)
        self.assertEqual(total_notes, 4)

    def test_refresh_note_qty(self):
        uid = 1
        with engine.connect() as connection:
            row = connection.execute('SELECT max(uid) FROM user_profiles').fetchone()
            uid = row[0] + 1
        u = User(logger=L)
        u.user_alias = 'user{}'.format(uid)
        u.user_email_address = 'user{}@example.tld'.format(uid)
        u.account_status = 1
        u.create_user_profile()
        uid = u.uid
        timestamps = list()
        for nid in range(1, 5):
            n = Note(logger=L)
            n.note_timestamp = int('1{}1{}0'.format(u.uid, nid))
            n.note_text = 'Note nr {} for user {}'.format(nid, u.uid)
            n.uid = u.uid
            n.create_note()
            timestamps.append(n.note_timestamp)
        self.assertEqual(len(timestamps), 4)
        note = Note(logger=L)
        note.uid = uid
        note.load_note(note_timestamp=timestamps[1])
        note.delete_note()
        n = Notes(logger=L)
        n.uid = uid
        n.refresh_note_qty()
        self.assertEqual(n.total_notes_qty, 3)

# EOF

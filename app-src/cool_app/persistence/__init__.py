'''
This is the package persistence initialization and is abstracted from the rest of the application by using "sqlalchemy" ORM.

If you decide to use another RDMS system, you would only need to change this file, and more specifically update the "engine" initialization
'''
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import traceback
import sys
import os
from cool_app import ServiceLogger
from circuitbreaker import circuit


L = ServiceLogger()
engine = None
try:
    engine = create_engine(
        'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
            os.getenv('DB_USER', 'postgres'),
            os.getenv('DB_PASS', 'password'),
            os.getenv('DB_HOST', 'localhost'),
            os.getenv('DB_PORT', '5432'),
            os.getenv('DB_NAME', 'coolapp')
        ),
        isolation_level="READ UNCOMMITTED"
    )
except:                                                                 # pragma: no cover
    L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))     # pragma: no cover
    engine = None                                                       # pragma: no cover


def test_data_source(L: ServiceLogger=L)->bool:
    '''
        A handy helper function that can be used to validate the database connection and that the tables have been created.
    '''
    working = False
    try:
        if engine is not None:
            with engine.connect() as connection:
                result = connection.execute("select uid from user_profiles").fetchone()
                if result:
                    working = True
                    L.info(message='test_data_source(): result "{}"'.format(result))
                else:
                    L.info(message='test_data_source(): connection appears to have succeeded but there is no data')
        else:
            L.info(message='test_data_source(): engine not defined')
    except:
        L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    return working


@circuit(failure_threshold=1)
def db_test_without_try_block(f_engine=engine, L: ServiceLogger=L, use_invalid_sql: bool=False)->bool:
    '''
        This function will still trigger the circuit breaker on an invalid SQL statement, even though the connections is fine.

        This is not what we want. The Circuit breaker must only kick in when there is an issue with the actual SQL connections.
    '''
    with f_engine.connect() as connection:
        result = None
        if use_invalid_sql:
            result = connection.execute(text('SELECT * from I_DONT_EXIST;')).fetchone()
        else:
            result = connection.execute(text('SELECT 1+1;')).fetchone()
        L.debug(message='value={}'.format(result[0]))
    return True


@circuit(failure_threshold=1)
def db_test_with_try_block(f_engine=engine, L: ServiceLogger=L, use_invalid_sql: bool=False)->bool:
    '''
        This example is the EXPECTED behavior - the circuit breaker only triggers if there is a connectivity issue, regardless of the valid SQL or not.
    '''
    with f_engine.connect() as connection:
        try:
            result = None
            if use_invalid_sql:
                result = connection.execute(text('SELECT * from I_DONT_EXIST;')).fetchone()
            else:
                result = connection.execute(text('SELECT 1+1;')).fetchone()
            L.debug(message='value={}'.format(result[0]))
        except:
            L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    return True


'''
    #region USER PROFILE SECTION
'''

@circuit(failure_threshold=1)
def db_create_user_profile(user_alias: str, user_email_address: str, account_status: int=0, f_engine=engine, L: ServiceLogger=L)->bool:
    with f_engine.connect() as connection:
        try:
            result = connection.execute(text('INSERT INTO user_profiles ( user_alias, user_email_address, account_status ) VALUES ( :f1, :f2, :f3 )'), f1=user_alias, f2=user_email_address, f3=account_status)
            L.debug(message='result={}'.format(result))
        except:
            L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    return True


@circuit(failure_threshold=1)
def db_load_user_profile_by_email_address(user_email_address, f_engine=engine, L: ServiceLogger=L)->dict:
    profile = dict()
    with f_engine.connect() as connection:
        try:
            result = connection.execute(text('SELECT uid, user_alias, user_email_address, account_status FROM user_profiles WHERE user_email_address = :f1'), f1=user_email_address).fetchone()
            L.debug(message='result={}'.format(result))
            if result:
                profile['uid'] = result['uid']
                profile['user_alias'] = result['user_alias']
                profile['user_email_address'] = result['user_email_address']
                profile['account_status'] = result['account_status']
        except:
            L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    return profile


@circuit(failure_threshold=1)
def db_load_user_profile_by_uid(uid: int, f_engine=engine, L: ServiceLogger=L)->dict:
    profile = dict()
    with f_engine.connect() as connection:
        try:
            result = connection.execute(text('SELECT uid, user_alias, user_email_address, account_status FROM user_profiles WHERE uid = :f1'), f1=uid).fetchone()
            L.debug(message='result={}'.format(result))
            if result:
                profile['uid'] = result['uid']
                profile['user_alias'] = result['user_alias']
                profile['user_email_address'] = result['user_email_address']
                profile['account_status'] = result['account_status']
        except:
            L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    return profile


@circuit(failure_threshold=1)
def db_update_user_profile(user_alias: str, user_email_address: str, uid:int, account_status: int, f_engine=engine, L: ServiceLogger=L)->bool:
    with f_engine.connect() as connection:
        try:
            result = connection.execute(text('UPDATE user_profiles SET user_alias = :f1, user_email_address = :f2, account_status = :f3 WHERE uid = :f4'), f1=user_alias, f2=user_email_address, f3=account_status, f4=uid)
            L.debug(message='result={}'.format(result))
        except:
            L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    return True

'''
    #endregion
'''

'''
    #region NOTES SECTION
'''

@circuit(failure_threshold=1)
def db_get_all_notes_from_timestamp(uid: int, start_timestamp: int=0, limit: int=20, order_descending: bool=False, f_engine=engine, L: ServiceLogger=L)->tuple:
    timestamps = list()
    notes = list()
    with f_engine.connect() as connection:
        order = 'ASC'
        if order_descending is True:
            order = 'DESC'
        try:
            for row in connection.execute(text('SELECT uid, note_timestamp, note_text FROM notes WHERE uid = :f1 AND note_timestamp >= :f2 ORDER BY note_timestamp {} LIMIT {}'.format(order, limit)), f1=uid, f2=start_timestamp).fetchall():
                L.debug(message='row={}'.format(row))
                note = dict()
                note['uid'] = row['uid']
                note['note_timestamp'] = int(row['note_timestamp'])
                note['note_text'] = row['note_text']
                timestamps.append(note['note_timestamp'])
                notes.append(note)
        except:
            L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    return (timestamps, notes)


@circuit(failure_threshold=1)
def db_get_notes_total_qty_for_user(uid: int, f_engine=engine, L: ServiceLogger=L)->list:
    result = list()
    with f_engine.connect() as connection:
        try:
            for row in connection.execute(text('SELECT note_timestamp FROM notes WHERE uid = :f1'), f1=uid).fetchall():
                result.append(row[0])
        except:
            L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    return result

'''
    #endregion
'''


'''
    #region NOTE SECTION
'''


@circuit(failure_threshold=1)
def db_create_note(uid: int, note_timestamp: int, note_text: str, f_engine=engine, L: ServiceLogger=L)->bool:
    with engine.connect() as connection:
        try:
            result = connection.execute(text('INSERT INTO notes ( uid, note_timestamp, note_text ) VALUES ( :f1, :f2, :f3 )'), f1=uid, f2=note_timestamp, f3=note_text)
            L.debug(message='result={}'.format(result))
        except:
            L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    return True


@circuit(failure_threshold=1)
def db_load_note(uid: int, note_timestamp: int, f_engine=engine, L: ServiceLogger=L)->dict:
    note = dict()
    with engine.connect() as connection:
        result = None
        try:
            result = connection.execute(text('SELECT uid, note_timestamp, note_text FROM notes WHERE uid = :f1 AND note_timestamp = :f2'), f1=uid, f2=note_timestamp).fetchone()
            L.debug(message='result={}'.format(result))
        except:
            L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
        if result:
            note['uid'] = result['uid']
            note['note_timestamp'] = result['note_timestamp']
            note['note_text'] = result['note_text']
    return note


@circuit(failure_threshold=1)
def db_update_note(updated_text: str, uid: int, note_timestamp: int, f_engine=engine, L: ServiceLogger=L)->bool:
    with f_engine.connect() as connection:
        try:
            result = connection.execute(text('UPDATE notes SET note_text = :f1 WHERE uid = :f2 AND note_timestamp = :f3'), f1=updated_text, f2=uid, f3=note_timestamp)
            L.debug(message='result={}'.format(result))
        except:
            L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    return True


'''
    #endregion
'''

# EOF

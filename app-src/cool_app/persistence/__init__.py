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
def db_create_user_profile(user_alias: str, user_email_address: str, account_status: int=0, f_engine=engine, L: ServiceLogger=L)->bool:
    with f_engine.connect() as connection:
        result = connection.execute(text('INSERT INTO user_profiles ( user_alias, user_email_address, account_status ) VALUES ( :f1, :f2, :f3 )'), f1=user_alias, f2=user_email_address, f3=account_status)
        L.debug(message='result={}'.format(result))
    return True


@circuit(failure_threshold=1)
def db_load_user_profile_by_email_address(user_email_address, f_engine=engine, L: ServiceLogger=L)->dict:
    profile = dict()
    with f_engine.connect() as connection:
        result = connection.execute(text('SELECT uid, user_alias, user_email_address, account_status FROM user_profiles WHERE user_email_address = :f1'), f1=user_email_address).fetchone()
        L.debug(message='result={}'.format(result))
        if result:
            profile['uid'] = result['uid']
            profile['user_alias'] = result['user_alias']
            profile['user_email_address'] = result['user_email_address']
            profile['account_status'] = result['account_status']
    return profile


@circuit(failure_threshold=1)
def db_load_user_profile_by_uid(uid: int, f_engine=engine, L: ServiceLogger=L)->dict:
    profile = dict()
    with f_engine.connect() as connection:
        result = connection.execute(text('SELECT uid, user_alias, user_email_address, account_status FROM user_profiles WHERE uid = :f1'), f1=uid).fetchone()
        L.debug(message='result={}'.format(result))
        if result:
            profile['uid'] = result['uid']
            profile['user_alias'] = result['user_alias']
            profile['user_email_address'] = result['user_email_address']
            profile['account_status'] = result['account_status']
    return profile


@circuit(failure_threshold=1)
def db_update_user_profile(user_alias: str, user_email_address: str, uid:int, account_status: int, f_engine=engine, L: ServiceLogger=L)->bool:
    with f_engine.connect() as connection:
        result = connection.execute(text('UPDATE user_profiles SET user_alias = :f1, user_email_address = :f2, account_status = :f3 WHERE uid = :f4'), f1=user_alias, f2=user_email_address, f3=account_status, f4=uid)
        L.debug(message='result={}'.format(result))
    return True


# EOF

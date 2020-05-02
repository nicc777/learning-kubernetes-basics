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
except:
    L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    engine = None


def test_data_source(L: ServiceLogger=L)->bool:
    '''
        A handy helper function that can be used to validate the database connection and that the tables have been created.
    '''
    working = False
    try:
        if engine is not None:
            with engine.connect() as connection:
                result = connection.execute("select uid from user_profiles")
                if result:
                    working = True
                    for row in result:
                        L.info(message='test_data_source(): found uid "{}"'.format(row[0]))
                else:
                    L.info(message='test_data_source(): connection appears to have succeeded but there is no data')
        else:
            L.info(message='test_data_source(): engine not defined')
    except:
        L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    return working



    

from sqlalchemy import create_engine
import traceback
import sys
import os


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
    traceback.print_exc(file=sys.stdout)
    engine = None


def test_data_source()->bool:
    working = False
    try:
        if engine is not None:
            with engine.connect() as connection:
                result = connection.execute("select uid from user_profiles")
                if result:
                    working = True
                    for row in result:
                        print('test_data_source(): found uid "{}"'.format(row[0]))
                else:
                    print('test_data_source(): connection appears to have succeeded but there is no data')
        else:
            print('test_data_source(): engine not defined')
    except:
        traceback.print_exc(file=sys.stdout)
    return working

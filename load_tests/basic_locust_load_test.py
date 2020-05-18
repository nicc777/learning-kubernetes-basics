import traceback
import sys
import os
import random
import json
from locust import HttpUser, task, between
from sqlalchemy import create_engine
from sqlalchemy.sql import text

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
    engine = None
    sys.exit(1)

test_users = list()
for i in range(1,int(os.getenv('MAX_USERS', '100'))):
    test_users.append(
        'lu{}@locust-test.tld'.format(i)
    )
uids = list()
notes = list()

with engine.connect() as connection:
    connection.execute(text('delete from notes where nid in (select a.nid from notes as a, user_profiles as b where a.uid = b.uid and b.user_email_address like \'%@locust-test.tld\')'))
    connection.execute(text('delete from user_profiles where user_email_address like \'%@locust-test.tld\''))

print('READY')


class WebsiteUser(HttpUser):
    wait_time = between(3, 6)

    @task(10)
    def get_user_profile(self):
        '''
            curl -X GET "http://192.168.0.160:8080/v1/user-profiles/1" -H "accept: application/json"
        '''
        print('FIRE get_user_profile()')
        if len(uids) > 0:
            uid = random.choice(uids)
            response = self.client.get('/v1/user-profiles/{}'.format(uid))
            # print('response.text={}'.format(response.text))

    @task(20)
    def get_user_notes_last_10(self):
        '''
           curl -X GET "http://192.168.0.160:8080/v1/notes/1?limit=10" -H "accept: application/json"
        '''
        print('FIRE get_user_notes_last_10()')
        if len(uids) > 0 and len(notes) > 0:
            uid = random.choice(uids)
            response = self.client.get('/v1/notes/{}?limit=10'.format(uid))
            # print('response.text={}'.format(response.text))

    @task(1)
    def create_new_user(self):
        '''
            curl -X POST "http://192.168.0.160:8080/v1/user-profiles" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"AccountStatus\":1,\"UserAlias\":\"lu02\",\"UserEmailAddress\":\"lu02@locust-test.tld\"}"
        '''
        print('FIRE create_new_user()')
        if len(test_users) > 0:
            email_address = test_users.pop(0)
            alias = email_address.split('@')[0].capitalize()
            payload = {'AccountStatus': 1, 'UserAlias': alias, 'UserEmailAddress': email_address}
            headers = {'Accept': 'application/json'}
            response = self.client.post("/v1/user-profiles", json=payload, headers=headers)
            # print('response.text={}'.format(response.text))
            response_data = json.loads(response.text)
            if 'Link' in response_data:
                uids.append(int(response_data['Link'].split('/')[-1]))
        print('QTY uids: {}'.format(len(uids)))

    @task(8)
    def create_new_note(self):
        '''
            curl -X POST "http://192.168.0.160:8080/v1/notes/2" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"NoteText\":\"Test 5\"}"
        '''
        print('FIRE create_new_note()')
        if len(uids) > 0:
            uid = random.choice(uids)
            payload = {'NoteText': 'This is note nr {} for user {}'.format(len(notes), uid)}
            notes.append(uid)
            headers = {'Accept': 'application/json'}
            response = self.client.post('/v1/notes/{}'.format(uid), json=payload, headers=headers)
            # print('response.text={}'.format(response.text))
        print('QTY notes: {}'.format(len(notes)))


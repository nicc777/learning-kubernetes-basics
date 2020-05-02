'''
Comments in this file will be verbose as it is intended as a learning tool

The cool-app is intended to demonstrate some cool features of microservices running in a typical Kubernetes cluster.

The following high-level features are implemented:

* Liveliness and readyness probes as suggested by Kubernetes - see https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
* Metrics collectors and API, using Redis as a backend
* Circuit-Breaker pattern to cater for cases where redis is not installed or otherwise unusable - see https://martinfowler.com/bliki/CircuitBreaker.html
'''

import socket
import traceback
import os
import sys
from datetime import datetime
import connexion
from cool_app import ServiceLogger
from cool_app.persistence.user_profiles import User


'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                       THREAD INITIALIZATION                          /////
/////                                                                      /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////'''


L = ServiceLogger()
SPECIFICATION_DIR = os.getenv('SPECIFICATION_DIR', '/usr/src/app')
L.info(message='Reading OpenAPI from file "{}"'.format(os.getenv('SPECIFICATION_DIR', '/opt/cool-app.yaml')))
start_time = int(datetime.now().timestamp())
app_version = '0.0.1'


'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                          HELPER FUNCTIONS                            /////
/////                                                                      /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////'''


def get_hostname():
    hostname = 'unknown2'
    try:
        hostname = socket.gethostname()
    except:
        traceback.print_exc(file=sys.stdout)
    return hostname


def uptime()->int:
    return int(datetime.now().timestamp()) - start_time


def generate_generic_error_response(error_code: int, error_message: str)->dict:
    return {
        'ErrorCode': error_code,
        'ErrorMessage': error_message
    }


'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                     REQUEST HANDLERS SECTION                         /////
/////                                                                      /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////'''


def search_user_profiles(email_address):
    http_response_code = 404
    result = generate_generic_error_response(error_code=404, error_message='User Profile Not Found')
    u = User(logger=L)
    if u.load_user_profile_by_email_address(user_email_address=email_address):
        result = dict()
        result['UserProfileLink'] = '/user-profiles/{}'.format(u.uid)
        result['UserId'] = u.uid
        result['UserAlias'] = u.user_alias
        result['UserEmailAddress'] = u.user_email_address
        result['AccountStatus'] = u.account_status
        http_response_code = 200
    return result, http_response_code


def get_user_profile(uid):
    http_response_code = 404
    result = generate_generic_error_response(error_code=404, error_message='User Profile Not Found')
    u = User(logger=L)
    if u.load_user_profile_by_uid(uid=uid):
        result = dict()
        result['UserProfileLink'] = '/user-profiles/{}'.format(u.uid)
        result['UserId'] = u.uid
        result['UserAlias'] = u.user_alias
        result['UserEmailAddress'] = u.user_email_address
        result['AccountStatus'] = u.account_status
        http_response_code = 200
    return result, http_response_code


'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                         APP SETUP SECTION                            /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////'''


options = {"swagger_ui": False}
if int(os.getenv('SWAGGER_UI', '1')) > 0:
    options = {"swagger_ui": True}    
app = connexion.FlaskApp(__name__, specification_dir=SPECIFICATION_DIR)
app.add_api('cool-app.yaml', strict_validation=True)
application = app.app # expose global WSGI application object

# EOF

'''
Comments in this file will be verbose as it is intended as a learning tool

This version of the application demonstrated a typical "legacy" REST application using a PostgreSQL database for persistence.
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
////////////////////////////////////////////////////////////////////////////////

Here we do some initialization stuff to set-up the application.

At this stage only a logger is set-up as well as the base path to our OpenAPI configuration
'''


L = ServiceLogger()
SPECIFICATION_DIR = os.getenv('SPECIFICATION_DIR', '/usr/src/app')
L.info(message='Reading OpenAPI from file "{}"'.format(os.getenv('SPECIFICATION_DIR', '/opt/cool-app.yaml')))


'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                          HELPER FUNCTIONS                            /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////

These are common functions that may be used within request handlers.

The basic criteria is to place any operation that repeat in more than one request handler here as a function
'''


def generate_generic_error_response(error_code: int, error_message: str)->dict:
    '''
        Response generator for the '#/components/schemas/UserProfileSearchResult' schema
    '''
    return {
        'ErrorCode': error_code,
        'ErrorMessage': error_message
    }


def prepare_user_profile_response(u: User)->dict:
    '''
        Response generator for the '#/components/schemas/GenericError' schema
    '''
    result = dict()
    result['UserProfileLink'] = '/user-profiles/{}'.format(u.uid)
    result['UserId'] = u.uid
    result['UserAlias'] = u.user_alias
    result['UserEmailAddress'] = u.user_email_address
    result['AccountStatus'] = u.account_status
    return result


'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                     REQUEST HANDLERS SECTION                         /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////'''


def search_user_profiles(email_address):
    '''
        Request Handler for path '/user-profiles/search'
    '''
    http_response_code = 404
    result = generate_generic_error_response(error_code=404, error_message='User Profile Not Found')
    u = User(logger=L)
    if u.load_user_profile_by_email_address(user_email_address=email_address):
        result = prepare_user_profile_response(u=u)
        http_response_code = 200
    return result, http_response_code


def get_user_profile(uid):
    '''
        Request Handler for path '/user-profiles/{uid}'
    '''
    http_response_code = 404
    result = generate_generic_error_response(error_code=404, error_message='User Profile Not Found')
    u = User(logger=L)
    if u.load_user_profile_by_uid(uid=uid):
        result = prepare_user_profile_response(u=u)
        http_response_code = 200
    return result, http_response_code


'''
////////////////////////////////////////////////////////////////////////////////
/////                                                                      /////
/////                         APP SETUP SECTION                            /////
/////                                                                      /////
////////////////////////////////////////////////////////////////////////////////

This is the connexion specific setup area and have to be at the end of the file.
'''


options = {"swagger_ui": False}
if int(os.getenv('SWAGGER_UI', '1')) > 0:
    options = {"swagger_ui": True}    
app = connexion.FlaskApp(__name__, specification_dir=SPECIFICATION_DIR)
app.add_api('cool-app.yaml', strict_validation=True)
#application = app.app # expose global WSGI application object

# EOF

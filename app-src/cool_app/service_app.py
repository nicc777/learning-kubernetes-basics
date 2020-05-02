'''
Comments in this file will be verbose as it is intended as a learning tool

This version of the application demonstrated a typical "legacy" REST application using a PostgreSQL database for 
persistence.
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


def general_success_response(message: str, link: str='', link_type: str='None')->dict:
    '''
        Response generator for the '#/components/schemas/GeneralSuccessSchema' schema
    '''
    result = dict()
    result['Message'] = message
    result['Link'] = link
    result['LinkType'] = link_type
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
        Request Handler for path '/user-profiles/{uid}' using a GET method
    '''
    http_response_code = 404
    result = generate_generic_error_response(error_code=404, error_message='User Profile Not Found')
    u = User(logger=L)
    if u.load_user_profile_by_uid(uid=uid):
        result = prepare_user_profile_response(u=u)
        http_response_code = 200
    return result, http_response_code


def update_user_profile(uid, body):
    '''
        Request Handler for path '/user-profiles/{uid}' using a PUT method
    '''
    http_response_code = 404
    result = generate_generic_error_response(error_code=404, error_message='User Profile Not Found')
    u = User(logger=L)
    if u.load_user_profile_by_uid(uid=uid):
        if body['FieldName'] == 'UserAlias':
            u.user_alias = body['FieldValue']
        elif body['FieldName'] == 'UserEmailAddress':
            u.user_email_address = body['FieldValue']
        elif body['FieldName'] == 'AccountStatus':
            u.user_email_address = int(body['FieldValue'])
        else:
            return generate_generic_error_response(
                error_code=404,
                error_message='The field to update could not be found'
            ), http_response_code
        if u.update_user_profile() is True:
            http_response_code = 201
            result = general_success_response(
                message='Field "{}" updated'.format(body['FieldName']),
                link='/user-profiles/{}'.format(u.uid),
                link_type='UserProfile'
            )
    return result, http_response_code


def new_user_profile(body):
    '''
        Request Handler for path '/user-profiles/new' using a POST method

        Note that this function is implemented in a idempotent way. No matter how many times you submit the same user 
        data to be created, if the record already exist, you will just get the persisted data back.

        The only caveat to the idempotent implementation is that if subsequent requests have different field values, 
        you will still get the response with the field values as persisted in the database - so perhaps not a 100% pure 
        idempotent implementation?

        This implementation differ from the official guidance at https://restfulapi.net/idempotent-rest-apis/ as the 
        database is keyed on e-mail address and we don't want multiple user profiles with the same e-mail address.
    '''
    http_response_code = 404
    result = generate_generic_error_response(error_code=500, error_message='Failed to create the user profile')
    u = User(logger=L)
    u.user_alias = body['UserAlias']
    u.user_email_address = '{}'.format(body['UserEmailAddress']).lower()
    if 'AccountStatus' in body:
        u.account_status = int(body['AccountStatus'])
    else:
        u.account_status = 0
    if u.create_user_profile():
        http_response_code = 201
        result = general_success_response(
            message='User with e-mail address "{}" created'.format(u.user_email_address),
            link='/user-profiles/{}'.format(u.uid), link_type='UserProfile'
        )
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

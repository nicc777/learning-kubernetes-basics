from sqlalchemy.sql import text
import traceback
import sys
import os
from cool_app import ServiceLogger
from cool_app.persistence import engine, db_create_user_profile, db_load_user_profile_by_email_address, db_load_user_profile_by_uid, db_update_user_profile


class User:

    '''
        The User class represents a user profile
    '''

    def __init__(
        self,
        logger: ServiceLogger=ServiceLogger(),
        engine=engine,
        db_create_user_profile_function=db_create_user_profile,
        db_load_user_profile_by_email_address_function=db_load_user_profile_by_email_address,
        db_load_user_profile_by_uid_function=db_load_user_profile_by_uid,
        db_update_user_profile_function=db_update_user_profile
    ):
        self.uid = None
        self.user_alias = None
        self.user_email_address = None
        self.account_status = None
        self.L = logger
        self.engine = engine
        self.db_create_user_profile_function = db_create_user_profile_function
        self.db_load_user_profile_by_email_address_function = db_load_user_profile_by_email_address_function
        self.db_load_user_profile_by_uid_function = db_load_user_profile_by_uid_function
        self.db_update_user_profile_function = db_update_user_profile_function

    def create_user_profile(self)->bool:
        '''
            The basic preparation steps you need to take before calling this function, that will create a new user profile, is:

            >>> u = User()
            >>> u.user_alias = 'FatCat'
            >>> u.user_email_address = 'user1@example.tld'
            >>> u.account_status = 1
            >>> if create_user_profile() is True:
            >>>     pass    # Handle success
            >>> else:
            >>>     pass    # Handle failure
        '''
        user_created = True
        self.L.info(message='Attempting to create user profile in database for user with e-mail address "{}"'.format(self.user_email_address))
        if self.uid is None and self.user_alias is not None and self.user_email_address is not None and self.account_status is not None:
            try:
                user_created = self.db_create_user_profile_function(
                    user_alias=self.user_alias,
                    user_email_address=self.user_email_address,
                    account_status=self.account_status,
                    L=self.L)
            except:
                self.L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
        else:
            self.L.warning(message='User profile appears to be already persisted. Nothing to do. uid={}'.format(self.uid))
        self.L.info(message='Final result: {}'.format(user_created))
        self.load_user_profile_by_email_address(user_email_address=self.user_email_address)
        return user_created

    def load_user_profile_by_email_address(self, user_email_address: str)->bool:
        '''
            Loads the user profile from the database based on the input email_address.

            A successful retrieval will set the other properties of the use in this class

            >>> u =User()
            >>> if u.load_user_profile_by_email_address(user_email_address='user1@example.tld'):
            >>>     pass    # Use the User object
            >>> else:
            >>>     pass    # Handle failure (profile did not load)
        '''
        user_loaded = False
        self.uid = None
        self.user_email_address = None
        self.user_alias = None
        self.account_status = None
        try:
            result = self.db_load_user_profile_by_email_address_function(user_email_address=user_email_address, L=self.L)
            self.L.debug(message='result={}'.format(result))
            if int(result['uid']) > 0:
                self.uid = result['uid']
                self.user_alias = result['user_alias']
                self.user_email_address = result['user_email_address']
                self.account_status = result['account_status']
                user_loaded = True
        except:
            self.L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
        return user_loaded

    def load_user_profile_by_uid(self, uid: int)->bool:
        '''
            Loads the user profile from the database based on the input uid.

            A successful retrieval will set the other properties of the use in this class

            >>> u =User()
            >>> if u.load_user_profile_by_uid(uid=123):
            >>>     pass    # Use the User object
            >>> else:
            >>>     pass    # Handle failure (profile did not load)
        '''
        user_loaded = False
        self.uid = None
        self.user_email_address = None
        self.user_alias = None
        self.account_status = None
        try:
            result = self.db_load_user_profile_by_uid_function(uid=uid, L=self.L)
            self.L.debug(message='result={}'.format(result))
            if int(result['uid']) > 0:
                self.uid = result['uid']
                self.user_alias = result['user_alias']
                self.user_email_address = result['user_email_address']
                self.account_status = result['account_status']
                user_loaded = True
        except:
            self.L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
        return user_loaded

    def update_user_profile(self)->bool:
        '''
            Updates the user profile. Write out all properties to the database.

            >>> u =User()
            >>> if u.load_user_profile_by_uid(uid=123):
            >>>     u.user_alias = 'SimplyTheBest'
            >>>     if u.update_user_profile():
            >>>         pass    # Use the updated User object with the new alias
            >>>     else:
            >>>         pass    # Handle failure (profile did not load)
            >>> else:
            >>>     pass    # Handle failure (profile did not load)
        '''
        user_updated = False
        try:
            user_updated = self.db_update_user_profile_function(user_alias=self.user_alias, user_email_address=self.user_email_address, uid=int(self.uid), account_status=int(self.account_status), L=self.L)
        except:
            self.L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
        return user_updated

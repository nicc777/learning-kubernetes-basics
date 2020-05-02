from sqlalchemy.sql import text
import traceback
import sys
import os
from cool_app import ServiceLogger
from cool_app.persistence import engine


class Note:
    '''
        The Note class is where a user's Note lives.
    '''

    def __init__(
        self,
        logger: ServiceLogger=ServiceLogger(),
        engine=engine
    ):
        self.uid = None
        self.note_timestamp = None
        self.note_text = None
        self.L = logger
        self.engine = engine
    
    def create_note(self)->bool:
        '''
            Creates a new note for the user

            Example:

                >>> note = Note()
                >>> note.uid = uid
                >>> note.note_text = 'hello world'
                >>> note.note_timestamp = 1234567890
                >>> if note.create_note() is True:
                >>>     pass # Process success state
                >>> else:
                >>>     pass # Process failed state

            There is not currently a elegant way to handle duplicate notes. The database implements a constraint to 
            prevent a user submitting the exact same text more than once. However, on Exception we do not have enough 
            contextual data to retrieve the existing record (yet). 

            FIXME: The above is an issue (but for the scenarios to solve - so it's intended at this point)
        '''
        note_created = False
        self.L.info(message='Attempting to create note in database')
        exception_caught = False
        try:
            if self.engine is not None:
                with engine.connect() as connection:
                    result = connection.execute(text('INSERT INTO notes ( uid, note_timestamp, note_text ) VALUES ( :f1, :f2, :f3 )'), f1=self.uid, f2=self.note_timestamp, f3=self.note_text)
                    self.L.debug(message='result={}'.format(result))
            else:
                self.L.error(message='Database engine not ready. User profile not persisted')
        except:
            self.L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
            self.L.error(message='CRITICAL: the new note could NOT be created')
            exception_caught = True
        if exception_caught is False:            
            if self.load_note(note_timestamp=self.note_timestamp):
                note_created = True
            self.L.debug(message='Final result: {}'.format(note_created))
        return note_created

    def load_note(self, note_timestamp: int)->bool:
        '''
            Loads a note for a user, given the note_timestamp

            Example:

                >>> note = Note()
                >>> note.uid = uid
                >>> if note.load_note(note_timestamp=note_timestamp):
                >>>     pass # Process success state
                >>> else:
                >>>     pass # Process failed state
        '''
        note_loaded = False
        self.note_text = None
        self.note_timestamp = None
        try:
            if self.engine is not None:
                with engine.connect() as connection:
                    result = connection.execute(text('SELECT uid, note_timestamp, note_text FROM notes WHERE uid = :f1 AND note_timestamp = :f2'), f1=self.uid, f2=note_timestamp).fetchone()
                    self.L.debug(message='result={}'.format(result))
                    if result:
                        self.uid = result['uid']
                        self.note_timestamp = result['note_timestamp']
                        self.note_text = result['note_text']
            else:
                self.L.error(message='Database engine not ready. User profile not loaded')
            if self.uid is not None and self.note_timestamp is not None and self.note_text is not None:
                note_loaded = True
        except:
            self.L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
        return note_loaded

    def update_note(self, updated_text: str)->bool:
        '''
            Updates a user's existing note

            Example:

                >>> note = Note()
                >>> note.uid = uid
                >>> if note.load_note(note_timestamp=note_timestamp) is True:
                >>>     note.note_text = body['NoteText']
                >>>     if note.update_note(updated_text='I am the best programmer ever!!') is True:
                >>>         pass # Process success state
                >>>     else:
                >>>         pass # Process failed state
                >>> else:
                >>>     pass # Process failed state
        '''
        note_updated = False
        try:
            if self.engine is not None:
                with engine.connect() as connection:
                    result = connection.execute(text('UPDATE notes SET note_text = :f1 WHERE uid = :f2 AND note_timestamp = :f3'), f1=updated_text, f2=self.uid, f3=self.note_timestamp)
                    self.L.debug(message='result={}'.format(result))
                    if result:
                        note_updated = True
            else:
                self.L.error(message='Database engine not ready. User profile not loaded')
        except:
            self.L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
        if self.load_note(note_timestamp=self.note_timestamp):
            if self.note_text == updated_text:
                note_updated = True
        return note_updated

    def delete_note(self):
        '''
            Deletes a note

            Example:

                >>> note = Note()
                >>> note.uid = 123
                >>> note.note_timestamp = 1234567890
                >>> note.delete_note()
        '''
        try:
            if self.engine is not None:
                with engine.connect() as connection:
                    result = connection.execute(text('DELETE FROM notes WHERE uid = :f1 AND note_timestamp = :f2'), f1=self.uid, f2=self.note_timestamp)
                    self.L.debug(message='result={}'.format(result))
                    self.uid = None
                    self.note_timestamp = None
                    self.note_text = None
            else:
                self.L.error(message='Database engine not ready. User profile not loaded')
        except:
            self.L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))


class Notes:

    def __init__(
        self,
        logger: ServiceLogger=ServiceLogger(),
        engine=engine
    ):
        self.uid = None
        self.notes = list()
        self.timestamps = list()
        self.total_notes_qty = 0
        self.L = logger
        self.engine = engine

    def load_notes(self, start_timestamp: int=0, limit: int=20, order_descending: bool=False)->tuple:
        notes_loaded = 0
        self.refresh_note_qty()
        try:
            if self.engine is not None:
                with engine.connect() as connection:
                    order = 'ASC'
                    if order_descending is True:
                        order = 'DESC'
                    for row in connection.execute(text('SELECT uid, note_timestamp, note_text FROM notes WHERE uid = :f1 AND note_timestamp >= :f2 ORDER BY note_timestamp {} LIMIT {}'.format(order, limit)), f1=self.uid, f2=start_timestamp).fetchall():
                        self.L.debug(message='row={}'.format(row))
                        note = Note()
                        note.uid = row['uid']
                        note.note_timestamp = int(row['note_timestamp'])
                        note.note_text = row['note_text']
                        self.timestamps.append(note.note_timestamp)
                        self.notes.append(note)
            else:
                self.L.error(message='Database engine not ready. User profile not loaded')
        except:
            self.L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
        return (notes_loaded, self.total_notes_qty)

    def refresh_note_qty(self)->int:
        try:
            if self.engine is not None:
                with engine.connect() as connection:
                    result = connection.execute(text('SELECT COUNT(*) AS qty FROM notes WHERE uid = :f1'), f1=self.uid).fetchone()
                    self.L.info(message='type(result)={}   result={}'.format(type(result), result))
                    self.total_notes_qty = int(result['qty'])
            else:
                self.L.error(message='Database engine not ready. User profile not loaded')
        except:
            self.L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
        return self.total_notes_qty


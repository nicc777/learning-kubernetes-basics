'''
This is the package initialization and here we specifically initialize a general logger for our application.
'''
import logging
import inspect
import random
import os
import traceback


def generate_trace_id()->str:
    '''
        If the application need to create trace ID's, this function can be used.
    '''
    return '{}-{}-{}'.format(
        random.randint(1000,9999),
        random.randint(1000,9999),
        random.randint(1000,9999)
    )


logger = logging.getLogger(__name__)
logger_level = logging.INFO
user_requested_log_level = os.getenv('LOG_LEVEL', 'INFO')
if user_requested_log_level.upper() == 'DEBUG':
    logger_level = logging.DEBUG
logger.setLevel(logger_level)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create file handler and set level to debug
fh = logging.FileHandler(filename=os.getenv('LOG_FILE', '.{}api.log'.format(os.sep)))
fh.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('\n--==>  %(asctime)s - %(levelname)s - %(message)s\n')

# add formatter to ch and fh
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# add ch and fh to logger
logger.addHandler(ch)
logger.addHandler(fh)


def id_caller()->list:
    '''
        A helper function that examines the stack to extract some details for better reporting during logging

        Afterall, you want to know where in your code an error occurred right?
    '''
    result = list()
    try:
        caller_stack = inspect.stack()[2]
        result.append(caller_stack[1].split(os.sep)[-1]) # File name
        result.append(caller_stack[2]) # line number
        result.append(caller_stack[3]) # function name
    except: # pragma: no cover
        print('EXCEPTION: {}'.format(traceback.format_exc()))
    return result


class ServiceLogger:
    '''
        An application specific general logging class.

        By default it will use the logging as initialized in this module, but you can also configure your own and pass it in during initialization.

        In your modules you will typically have:

            >>> from cool_app import ServiceLogger
            >>> L = ServiceLogger()
    '''

    def __init__(self, logger_impl=logger):
        '''
            Initialize the class. Optionally, you can pass your own logging configuration.
        '''
        self.debug_flag = True
        self.logger = logger_impl
    
    def _format_msg(self, stack_data: list, message: str, trace_id: str='no-trace-id')->str:
        '''
            This function is not intended to be called in your code. It's a helper within this class.

            This function handles the formatting of the message before it is send to the logging handlers.
        '''
        if message is not None:
            message = '{}'.format(
                message
            )
            if len(stack_data) == 3:
                if self.debug_flag is True:
                    message = '[{}] [{}:{}:{}] {}'.format(
                        trace_id,
                        stack_data[0],
                        stack_data[1],
                        stack_data[2],
                        message
                    )
            return message
        return 'NO_INPUT_MESSAGE'

    def info(self, message: str, **kwargs):
        '''
            Log an INFO message. Optionally, you cen set a trace_id parameter that will add the value to the log message.

            Example usage:

                >>> from cool_app import ServiceLogger, generate_trace_id
                >>> L = ServiceLogger()
                >>> test_nr = 5
                >>> L.info(message='This is test nr {}'.format(5))

                    ~ or with a trace id ~

                >>> from cool_app import ServiceLogger, generate_trace_id
                >>> L = ServiceLogger()
                >>> def some_function(param1: int, param2: int, L: ServiceLogger=L, trace_id: int=None):
                >>>     L.info(message='param1={} and param2={}'.format(param1, param2), trace_id=trace_id)
                >>> my_trace_id = generate_trace_id()
                >>> L.info(message='About to call a function', trace_id=my_trace_id)
                >>> some_function(param1=123, param2=456, L=L, trace_id=my_trace_id)
                >>> L.info(message='Done. All log messages will include the same trace_id', trace_id=my_trace_id)
        '''
        trace_id = None
        if 'trace_id' in kwargs:
            trace_id = kwargs['trace_id']
        message = self._format_msg(stack_data=id_caller(), message=message, trace_id=trace_id)
        self.logger.info(message)

    def debug(self, message: str, **kwargs):
        '''
            Log a DEBUG message. Optionally, you cen set a trace_id parameter that will add the value to the log message.

            Example usage:

                >>> from cool_app import ServiceLogger, generate_trace_id
                >>> L = ServiceLogger()
                >>> L.debug(message='This app just started. So far so good!')

                    ~ or with a trace id ~

                >>> from cool_app import ServiceLogger, generate_trace_id
                >>> L = ServiceLogger()
                >>> my_trace_id = generate_trace_id()
                >>> L.debug(message='Trace ID was set', trace_id=my_trace_id)
        '''
        trace_id = None
        if 'trace_id' in kwargs:
            trace_id = kwargs['trace_id']
        if self.debug_flag is True:
            message = self._format_msg(stack_data=id_caller(), message=message, trace_id=trace_id)
            self.logger.debug(message)

    def warning(self, message: str, **kwargs):
        '''
            Log a WARNING message. Optionally, you cen set a trace_id parameter that will add the value to the log message.

            Example usage:

                >>> from cool_app import ServiceLogger, generate_trace_id
                >>> L = ServiceLogger()
                >>> L.warn(message='This app does nothing useful')

                    ~ or with a trace id ~

                >>> from cool_app import ServiceLogger, generate_trace_id
                >>> L = ServiceLogger()
                >>> my_trace_id = generate_trace_id()
                >>> L.warn(message='This app still does nothing useful, but with a trace_id', trace_id=my_trace_id)
        '''
        trace_id = None
        if 'trace_id' in kwargs:
            trace_id = kwargs['trace_id']
        message = self._format_msg(stack_data=id_caller(), message=message, trace_id=trace_id)
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        '''
            Log an ERROR message, which can include a stacktrace (common pattern). Optionally, you cen set a trace_id parameter that will add the value to the log message.

            Example usage:

                >>> import traceback
                >>> from cool_app import ServiceLogger, generate_trace_id
                >>> L = ServiceLogger()
                >>> def buggy_function(L: ServiceLogger=L):
                >>>     raise Exception('Yes, its a bug')
                >>> try:
                >>>     buggy_function()
                >>> except:
                >>>     L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
                >>> L.info(message='We survived the error and this message will still be generated')

                    ~ or with a trace id ~

                >>> import traceback
                >>> from cool_app import ServiceLogger, generate_trace_id
                >>> my_trace_id = generate_trace_id()
                >>> L = ServiceLogger()
                >>> def buggy_function(L: ServiceLogger=L):
                >>>     raise Exception('Yes, its a bug')
                >>> try:
                >>>     buggy_function()
                >>> except:
                >>>     L.error(message='EXCEPTION: {}'.format(traceback.format_exc()), trace_id=my_trace_id)
                >>> L.info(message='We survived the error and this message will still be generated', trace_id=my_trace_id)
        '''
        trace_id = None
        if 'trace_id' in kwargs:
            trace_id = kwargs['trace_id']
        message = self._format_msg(stack_data=id_caller(), message=message, trace_id=trace_id)
        self.logger.error(message)


# EOF

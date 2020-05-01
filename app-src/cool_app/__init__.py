# Copyright (c) 2020. All rights reserved. Nico Coetzee <nicc777@gmail.com>
# Please check LICENSE.txt for licencing information or visit https://github.com/nicc777/flask-prod-docker

import logging
import inspect
import random
import os
import traceback


def generate_trace_id()->str:
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

    def __init__(self, logger_impl=logger):
        self.debug_flag = True
        self.logger = logger_impl
    
    def _format_msg(self, stack_data: list, message: str, trace_id: str='no-trace-id')->str:
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
        trace_id = None
        if 'trace_id' in kwargs:
            trace_id = kwargs['trace_id']
        message = self._format_msg(stack_data=id_caller(), message=message, trace_id=trace_id)
        self.logger.info(message)

    def debug(self, message: str, **kwargs):
        trace_id = None
        if 'trace_id' in kwargs:
            trace_id = kwargs['trace_id']
        if self.debug_flag is True:
            message = self._format_msg(stack_data=id_caller(), message=message, trace_id=trace_id)
            self.logger.debug(message)

    def warning(self, message: str, **kwargs):
        trace_id = None
        if 'trace_id' in kwargs:
            trace_id = kwargs['trace_id']
        message = self._format_msg(stack_data=id_caller(), message=message, trace_id=trace_id)
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        trace_id = None
        if 'trace_id' in kwargs:
            trace_id = kwargs['trace_id']
        message = self._format_msg(stack_data=id_caller(), message=message, trace_id=trace_id)
        self.logger.error(message)


# EOF

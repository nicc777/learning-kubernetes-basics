import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import unittest
from cool_app import ServiceLogger
from tests import DummyLogger


class TestServiceLogger(unittest.TestCase):

    def test_service_logger_init_with_defaults_working(self):
        L = ServiceLogger()
        self.assertIsNotNone(L)

    def test_service_logger_init_with_dummy_logger_class(self):
        L = ServiceLogger(logger_impl=DummyLogger())
        self.assertIsNotNone(L)

    def test_service_logger_info_logs_with_dummy_logger_class(self):
        logger = DummyLogger()
        L = ServiceLogger(logger_impl=logger)
        L.info(message='TEST MESSAGE')
        self.assertEqual(len(logger.log_lines), 1)
        self.assertTrue(logger.log_lines[0].endswith('TEST MESSAGE'))

    def test_service_logger_debug_logs_with_dummy_logger_class(self):
        logger = DummyLogger()
        L = ServiceLogger(logger_impl=logger)
        L.debug(message='TEST MESSAGE')
        self.assertEqual(len(logger.log_lines), 1)
        self.assertTrue(logger.log_lines[0].endswith('TEST MESSAGE'))

    def test_service_logger_warning_logs_with_dummy_logger_class(self):
        logger = DummyLogger()
        L = ServiceLogger(logger_impl=logger)
        L.warning(message='TEST MESSAGE')
        self.assertEqual(len(logger.log_lines), 1)
        self.assertTrue(logger.log_lines[0].endswith('TEST MESSAGE'))

    def test_service_logger_error_logs_with_dummy_logger_class(self):
        logger = DummyLogger()
        L = ServiceLogger(logger_impl=logger)
        L.error(message='TEST MESSAGE')
        self.assertEqual(len(logger.log_lines), 1)
        self.assertTrue(logger.log_lines[0].endswith('TEST MESSAGE'))

# EOF

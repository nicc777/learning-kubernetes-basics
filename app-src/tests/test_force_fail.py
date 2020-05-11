import unittest

class TestForceFail(unittest.TestCase):
    
    def test_fail(self):
        '''
            To force a failure, which is handy to test your Jenkins jobs, uncomment the line below.
        '''
        self.assertTrue(False)
        self.assertTrue(True)

# EOF

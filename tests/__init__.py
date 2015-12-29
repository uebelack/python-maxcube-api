import unittest
import tests.test_cube

def maxcube_suite():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_cube)
    return suite
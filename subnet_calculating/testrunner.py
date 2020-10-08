"""Python 3.7. Launch all tests."""
import unittest

testmodules = ['test_subnet_IPv4', 'test_subnet_IPv6', 'test_launcher']

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for tm in testmodules:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(tm))
    unittest.TextTestRunner().run(suite)

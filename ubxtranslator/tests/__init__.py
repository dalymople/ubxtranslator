import unittest

from . import test_core, test_fields


def suite():
    suite = unittest.TestSuite()

    # test fields
    suite.addTest(test_fields.PadFieldTester())
    suite.addTest(test_fields.UbxFieldTester())
    suite.addTest(test_fields.UbxBitSubFieldTester())
    suite.addTest(test_fields.UbxBitFieldTester())

    # test core
    suite.addTest(test_core.UbxMsgTester())
    suite.addTest(test_core.UbxClsTester())
    suite.addTest(test_core.UbxParserTester())

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

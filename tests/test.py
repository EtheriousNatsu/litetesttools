#!/usr/bin/env python
# encoding: utf-8
# @version: 2.7
# @author: 'john'
# @time: 2017/11/12 下午11:37
# @contact: zhouqiang847@gmail.com


from testtools import testcase
import unittest


class TestTestCase(testcase.TestCase):
    def test_a(self):
        pass

    @testcase.skip("this is a test")
    def test_b(self):
        pass

    @testcase.skipIf(True, 'skip if test')
    def test_c(self):
        raise AssertionError()

    @testcase.skipUnless(False, 'skip unless test')
    def test_d(self):
        pass

    def test_e(self):
        raise Exception('Exception test')

    @testcase.expectedFailure
    def test_f(self):
        pass

    @testcase.expectedFailure
    def test_g(self):
        raise AssertionError()

if __name__ == '__main__':
    suit = unittest.TestLoader().loadTestsFromTestCase(TestTestCase)
    unittest.TextTestRunner(verbosity=2).run(suit)

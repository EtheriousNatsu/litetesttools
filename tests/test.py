#!/usr/bin/env python
# encoding: utf-8
# @version: 2.7
# @author: 'john'
# @time: 2017/11/12 下午11:37
# @contact: zhouqiang847@gmail.com


import unittest
from unittest import TestResult

from testtools import testcase
from testtools import runtest
from testtools.testcase import run_test_with

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

    def test_h(self):
        class FooRunTest(runtest.RunTest):
            def __init__(self, case, handlers=None, bar=None):
                super(FooRunTest, self).__init__(case, handlers)
                self.bar = bar
            def run(self, result=None):
                return self.bar
        class SomeCase(testcase.TestCase):
            @run_test_with(FooRunTest, bar='k')
            def test_foo(self):
                pass
        result = TestResult()
        case = SomeCase('test_foo')
        from_run_test = case.run(result)
        assert from_run_test == 'k'

if __name__ == '__main__':
    suit = unittest.TestLoader().loadTestsFromTestCase(TestTestCase)
    unittest.TextTestRunner(verbosity=2).run(suit)

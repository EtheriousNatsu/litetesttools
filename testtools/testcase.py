#!/usr/bin/env python
# encoding: utf-8
# @version: 2.7
# @author: 'john'
# @time: 2017/10/23 上午12:43
# @contact: zhouqiang847@gmail.com

import unittest
from unittest import TestResult
import functools
import sys

from runtest import RunTest


class TestSkipped(Exception):
    """Raised within TestCase.run() when a test is skipped."""


class _UnexpectedSuccess(Exception):
    """An unexpected success was raised.

    Note that this exception is private plumbing in testtools' testcase
    module.
    """


class _ExpectedFailure(Exception):
    """An expected failure occured.

    Note that this exception is private plumbing in testtools' testcase
    module.
    """


def skip(reason):
    """A decorator to skip unit tests.

    This is just syntactic sugar so users don't have to change any of their
    unit tests in order to migrate to python 2.7, which provides the
    @unittest.skip decorator.
    """

    def decorator(test_item):
        # This attribute signals to RunTest._run_core that the entire test
        # must be skipped - including setUp and tearDown. This makes us
        # compatible with testtools.skip* functions, which set the same
        # attributes.
        test_item.__unittest_skip__ = True
        test_item.__unittest_skip_why__ = reason

        @functools.wraps(test_item)
        def skip_wrapper(*args, **kwargs):
            raise TestCase.skipException(reason)

        return skip_wrapper

    return decorator


def skipIf(condition, reason):
    """A decorator to skip a test if the condition is true."""
    if condition:
        return skip(reason)

    def _id(obj):
        return obj

    return _id


def skipUnless(condition, reason):
    """A decorator to skip a test unless the condition is true."""
    if not condition:
        return skip(reason)

    def _id(obj):
        return obj

    return _id


def expectedFailure(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            raise _ExpectedFailure(sys.exc_info())
        raise _UnexpectedSuccess

    return wrapper


def run_test_with(test_runner, **kwargs):
    """Decorate a test as using a specific ``RunTest``.

    e.g.::

      @run_test_with(CustomRunner, timeout=42)
      def test_foo(self):
          self.assertTrue(True)

    :param test_runner: A ``RunTest`` factory that takes a test case and an
        optional list of exception handlers.  See ``RunTest``.
    :param kwargs: Keyword arguments to pass on as extra arguments to
        'test_runner'.
    :return: A decorator to be used for marking a test as needing a special
        runner.
    """

    def decorator(function):
        # Set an attribute on 'function' which will inform TestCase how to
        # make the runner.
        def _run_test_with(case, handlers=None):
            return test_runner(case, handlers=handlers, **kwargs)

        function._run_test_with = _run_test_with
        return function

    return decorator


class TestCase(unittest.TestCase):
    """Extensions to the basic TestCase."""

    skipException = TestSkipped

    run_tests_with = RunTest

    def __init__(self, *args, **kwargs):
        """Construct a TestCase."""
        runTest = kwargs.pop('runTest', None)
        super(TestCase, self).__init__(*args, **kwargs)
        test_method = self._get_test_method()
        if runTest is None:
            runTest = getattr(test_method, '_run_test_with', self.run_tests_with)
        self.__RunTest = runTest

        self.exception_handlers = [
            (self.skipException, self._report_skip),
            (self.failureException, self._report_failure),
            (_ExpectedFailure, self._report_expected_failure),
            (_UnexpectedSuccess, self._report_unexpected_success),
            (Exception, self._report_error),
        ]

    def run(self, result=None):
        run_test = self.__RunTest(
            self, self.exception_handlers
        )
        return run_test.run(result)

    def _get_test_method(self):
        method_name = getattr(self, '_testMethodName')
        return getattr(self, method_name)

    def _run_test_method(self, result):
        """Run the test method for this test.

        :param result: A testtools.TestResult to report activity to.
        :return: None.
        """
        return self._get_test_method()()

    def _run_setup(self, result):
        """Run the setUp function for this test."""
        return self.setUp()

    def _run_teardown(self, result):
        """Run the tearDown function for this test."""
        return self.tearDown()

    def defaultTestResult(self):
        return TestResult()

    @staticmethod
    def _report_skip(self, result, reason):
        result.addSkip(self, reason)

    @staticmethod
    def _report_failure(self, result, err):
        result.addFailure(self, err)

    @staticmethod
    def _report_expected_failure(self, result, err):
        result.addExpectedFailure(self, err)

    @staticmethod
    def _report_unexpected_success(self, result, err):
        result.addUnexpectedSuccess(self)

    @staticmethod
    def _report_error(self, result, err):
        result.addError(self, err)

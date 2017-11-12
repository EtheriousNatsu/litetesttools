#!/usr/bin/env python
# encoding: utf-8
# @version: 2.7
# @author: 'john'
# @time: 2017/10/23 上午12:43
# @contact: zhouqiang847@gmail.com

import sys


class RunTest(object):
    """An object to run a test."""

    def __init__(self, case, handlers):
        """
        :param case: A testtools.TestCase test case object.
        :param handlers: Exception handlers for this RunTest. These are stored
            in self.handlers and can be modified later if needed.
        """
        self.case = case
        self.handlers = handlers
        self.exception_caught = object()
        self._exceptions = []

    def run(self, result):
        """Run self.case reporting activity to result.

        :param result: Optional testtools.TestResult to report activity to.
        :return: The result object the test was run against.
        """
        result.startTest(self.case)
        self.result = result
        try:
            self._exceptions = []
            self._run_core()
            if self._exceptions:
                # One or more caught exceptions, now trigger the test's
                # reporting method for just one.
                e = self._exceptions.pop()
                for exc_class, handler in self.handlers:
                    if isinstance(e[1], exc_class):
                        handler(self.case, self.result, e)
                        break
        finally:
            result.stopTest(self.case)

        return result

    def _run_core(self):
        """Run the user supplied test code."""
        test_method = self.case._get_test_method()
        if getattr(test_method, '__unittest_skip__', False):
            self.result.addSkip(
                self.case,
                reason=getattr(test_method, '__unittest_skip_why__', None)
            )
            return

        if self.exception_caught == self._run_user(self.case._run_setup,
                                                   self.result):
            # Don't run the test method if we failed getting here.
            self._run_cleanups(self.result)
            return

        # Run everything from here on in. If any of the methods raise an
        # exception we'll have failed.
        failed = False
        try:
            if self.exception_caught == self._run_user(
                    self.case._run_test_method, self.result):
                failed = True
        finally:
            try:
                if self.exception_caught == self._run_user(
                        self.case._run_teardown, self.result):
                    failed = True
            finally:
                try:
                    if self.exception_caught == self._run_user(
                            self._run_cleanups, self.result):
                        failed = True
                finally:
                    if getattr(self.case, 'force_failure', None):
                        self._run_user(_raise_force_fail_error)
                        failed = True
                    if not failed:
                        self.result.addSuccess(self.case)

    def _run_user(self, fn, *args, **kwargs):
        """Run a user supplied function.

        Exceptions are processed by `_got_user_exception`.

        :return: Either whatever 'fn' returns or ``exception_caught`` if
            'fn' raised an exception.
        """
        try:
            return fn(*args, **kwargs)
        except:
            return self._got_user_exception(sys.exc_info())

    def _run_cleanups(self, result):
        """Run the cleanups that have been added with addCleanup.

        See the docstring for addCleanup for more information.

        :return: None if all cleanups ran without error,
            ``exception_caught`` if there was an error.
        """
        failing = False
        while self.case._cleanups:
            function, arguments, keywordArguments = self.case._cleanups.pop()
            got_exception = self._run_user(
                function, *arguments, **keywordArguments)
            if got_exception == self.exception_caught:
                failing = True
        if failing:
            return self.exception_caught

    def _got_user_exception(self, exc_info):
        """Called when user code raises an exception.

        :param exc_info: A sys.exc_info() tuple for the user error.
        :return: 'exception_caught' if we catch one of the exceptions that
            have handlers in 'handlers', otherwise raise the error.
        """
        try:
            e = exc_info
        finally:
            del exc_info
        self._exceptions.append(e)
        # Yes, this means we catch everything - we re-raise KeyBoardInterrupt
        # etc later, after tearDown and cleanUp - since those may be cleaning up
        # external processes.
        return self.exception_caught

def _raise_force_fail_error():
    raise AssertionError("Forced Test Failure")
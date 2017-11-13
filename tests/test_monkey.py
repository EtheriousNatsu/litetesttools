#!/usr/bin/env python
# encoding: utf-8
# @version: 2.7
# @author: 'john'
# @time: 2017/11/13 下午10:10
# @contact: zhouqiang847@gmail.com


from testtools.monkey import MonkeyPatcher
from testtools.testcase import TestCase


class TestObj:
    def __init__(self):
        self.foo = 'foo value'
        self.bar = 'bar value'
        self.baz = 'baz value'


class MonkeyPatcherTest(TestCase):
    """
    Tests for 'MonkeyPatcher' monkey-patching class.
    """

    def setUp(self):
        super(MonkeyPatcherTest, self).setUp()
        self.test_object = TestObj()
        self.original_object = TestObj()
        self.monkey_patcher = MonkeyPatcher()


    def test_construct_with_patches(self):
        # Constructing a 'MonkeyPatcher' with patches adds all of the given
        # patches to the patch list.
        patcher = MonkeyPatcher((self.test_object, 'foo', 'haha'),
                                (self.test_object, 'bar', 'hehe'))
        patcher.patch()
        self.assertEquals('haha', self.test_object.foo)
        self.assertEquals('hehe', self.test_object.bar)
        self.assertEquals(self.original_object.baz, self.test_object.baz)

    def test_restore_non_existing(self):
        # Restoring a value that didn't exist before the patch deletes the
        # value.
        self.monkey_patcher.add_patch(self.test_object, 'doesntexist', 'value')
        self.monkey_patcher.patch()
        self.monkey_patcher.restore()
        marker = object()
        self.assertIs(marker, getattr(self.test_object, 'doesntexist', marker))


    def test_repeated_run_with_patches(self):
        # We can call the same function with run_with_patches more than
        # once. All patches apply for each call.
        def f():
            return (self.test_object.foo, self.test_object.bar,
                    self.test_object.baz)

        self.monkey_patcher.add_patch(self.test_object, 'foo', 'haha')
        result = self.monkey_patcher.run_with_patches(f)
        self.assertEquals(
            ('haha', self.original_object.bar, self.original_object.baz),
            result)
        result = self.monkey_patcher.run_with_patches(f)
        self.assertEquals(
            ('haha', self.original_object.bar, self.original_object.baz),
            result)
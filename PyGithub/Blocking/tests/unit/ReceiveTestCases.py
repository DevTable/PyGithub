# -*- coding: utf-8 -*-

# Copyright 2013-2014 Vincent Jacques <vincent@vincent-jacques.net>

import datetime
import sys
import unittest

import MockMockMock

import PyGithub.Blocking
import PyGithub.Blocking._paginated_list as pgl
import PyGithub.Blocking._receive as rcv


stringName = "str" if sys.hexversion >= 0x03000000 else "basestring"


class AttributeTestCase(unittest.TestCase):
    def setUp(self):
        self.mocks = MockMockMock.Engine()
        self.conv = self.mocks.create("conv")
        self.conv.expect.desc.andReturn("desc")
        self.log = self.mocks.replace("rcv.log")
        self.a = rcv.Attribute("name", self.conv.object, rcv.Absent)

    def tearDown(self):
        self.mocks.tearDown()

    def testName(self):
        self.assertEqual(self.a.name, "name")

    def testValueBeforeUpdate(self):
        self.assertEqual(self.a.value, None)

    def testUpdateAttributeWithAbsent(self):
        self.a.update(rcv.Absent)

        self.assertEqual(self.a.value, None)

    def testUpdateAttributeWithNone(self):
        self.a.update(None)

        self.assertEqual(self.a.value, None)

    def testUpdateAttributeWithValidValue(self):
        self.conv.expect(None, 42).andReturn(42)

        self.a.update(42)

        self.assertEqual(self.a.value, 42)
        self.assertFalse(self.a.needsLazyCompletion)

    def testUpdateAttributeWithArgsAndKwds(self):
        self.conv.expect(None, 42, 43, foo=44).andReturn(42)

        self.a.update(42, 43, foo=44)

        self.assertEqual(self.a.value, 42)
        self.assertFalse(self.a.needsLazyCompletion)

    def testUpdateAttributeWithValidValueThenAbsent(self):
        self.conv.expect(None, 42).andReturn(42)

        self.a.update(42)
        self.a.update(rcv.Absent)

        self.assertEqual(self.a.value, 42)

    def testUpdateAttributeWithValidValueThenNone(self):
        self.conv.expect(None, 42).andReturn(42)

        self.a.update(42)
        self.a.update(None)

        self.assertEqual(self.a.value, None)

    def testUpdateAttributeWithInvalidValue(self):
        e = rcv._ConversionException()
        self.conv.expect(None, 42).andRaise(e)
        self.log.expect.warn("Attribute name is expected to be a desc but GitHub API v3 returned 42")

        self.a.update(42)

        with self.assertRaises(PyGithub.Blocking.BadAttributeException) as cm:
            self.a.value
        self.assertEqual(cm.exception.args, ("name", "desc", 42, e))
        self.assertFalse(self.a.needsLazyCompletion)

    def testUpdateTwice(self):
        v = []
        self.conv.expect(None, 42).andReturn(v)
        self.conv.expect(v, 43).andReturn(v)

        self.a.update(42)
        self.a.update(43)

        self.assertIs(self.a.value, v)

    def testUpdateAfterException(self):
        v = []
        self.conv.expect(None, 42).andReturn(v)
        self.conv.expect(v, 43).andRaise(rcv._ConversionException())
        self.log.expect.warn("Attribute name is expected to be a desc but GitHub API v3 returned 43")
        self.conv.expect(v, 44).andReturn(v)

        self.a.update(42)
        self.a.update(43)
        self.a.update(44)

        self.assertIs(self.a.value, v)

    def testNeedsLazyCompletion(self):
        self.assertTrue(self.a.needsLazyCompletion)


class BuiltinConverterTestCase(unittest.TestCase):
    def testIntegerConverterDescription(self):
        self.assertEqual(rcv.IntConverter.desc, "Integral")

    def testIntegerConversion(self):
        self.assertEqual(rcv.IntConverter(None, 42), 42)

    def testLongConversion(self):
        self.assertEqual(rcv.IntConverter(None, 999999999999), 999999999999)

    def testBadIntegerConversion(self):
        with self.assertRaises(rcv._ConversionException):
            rcv.IntConverter(None, "42")

    def testStringConverterDescription(self):
        self.assertEqual(rcv.StringConverter.desc, stringName)

    def testStringConversion(self):
        self.assertEqual(rcv.StringConverter(None, "42"), "42")

    def testBadStringConversion(self):
        with self.assertRaises(rcv._ConversionException):
            rcv.StringConverter(None, 42)

    def testDatetimeConverterDescription(self):
        self.assertEqual(rcv.DatetimeConverter.desc, "datetime")

    def testDatetimeConversionFromInt(self):
        self.assertEqual(rcv.DatetimeConverter(None, 1395971262), datetime.datetime(2014, 3, 28, 1, 47, 42))

    def testDatetimeConversionFromString(self):
        self.assertEqual(rcv.DatetimeConverter(None, "2010-07-09T06:10:06Z"), datetime.datetime(2010, 7, 9, 6, 10, 6))

    def testBadDatetimeConversion(self):
        with self.assertRaises(rcv._ConversionException):
            rcv.DatetimeConverter(None, 4.5)

    def testBadDatetimeConversionFromString(self):
        with self.assertRaises(rcv._ConversionException):
            rcv.DatetimeConverter(None, "foobar")


class ListConverterTestCase(unittest.TestCase):
    def setUp(self):
        self.mocks = MockMockMock.Engine()
        self.content = self.mocks.create("content")
        self.conv = rcv.ListConverter(self.content.object)

    def tearDown(self):
        self.mocks.tearDown()

    def testDescription(self):
        self.content.expect.desc.andReturn("desc")
        self.assertEqual(self.conv.desc, "list of desc")

    def testGoodConversion(self):
        self.content.expect(None, 42).andReturn("42")
        self.content.expect(None, 43).andReturn("43")

        self.assertEqual(self.conv(None, [42, 43]), ["42", "43"])

    def testNotAList(self):
        with self.assertRaises(rcv._ConversionException):
            self.conv(None, 42)

    def testBadElement(self):
        self.content.expect(None, 42).andReturn("42")
        self.content.expect(None, 43).andRaise(rcv._ConversionException())

        with self.assertRaises(rcv._ConversionException):
            self.conv(None, [42, 43, 44])

    def testSecondConversionWithDifferentLength(self):
        self.content.expect(None, 44).andReturn("44")
        self.content.expect(None, 45).andReturn("45")

        instance = []
        ret = self.conv(instance, [44, 45])
        self.assertEqual(ret, ["44", "45"])
        self.assertIs(ret, instance)

    def testSecondConversionWithSameLength(self):
        self.content.expect(1, 44).andReturn("44")
        self.content.expect(2, 45).andReturn("45")

        instance = [1, 2]
        ret = self.conv(instance, [44, 45])
        self.assertEqual(ret, ["44", "45"])
        self.assertIs(ret, instance)

    def testConversionWithBadPreviousValue(self):
        l = self.conv("bad", [])
        self.assertEqual(l, [])


class StructureConverterTestCase(unittest.TestCase):
    class TheStruct(object):
        def __init__(self, session, attributes):
            self.Session = session
            self.__foo = rcv.Attribute("TheStruct.foo", rcv.StringConverter, rcv.Absent)
            self._updateAttributes(**attributes)

        @property
        def foo(self):
            return self.__foo.value

        def _updateAttributes(self, foo=rcv.Absent, **kwds):
            self.__foo.update(foo)

    def setUp(self):
        self.session = object()
        self.conv = rcv.StructureConverter(self.session, self.TheStruct)

    def testDescription(self):
        self.assertEqual(self.conv.desc, "TheStruct")

    def testConversion(self):
        instance = self.conv(None, {"foo": "bar"})
        self.assertEqual(instance.foo, "bar")
        self.assertIs(instance.Session, self.session)

    def testConversionFromEmptyDict(self):
        instance = self.conv(None, {})
        self.assertEqual(instance.foo, None)

    def testConversionWithUnexpectedKeys(self):
        instance = self.conv(None, {"toto": "tutu"})
        self.assertEqual(instance.foo, None)

    def testConversionWithBadPreviousValue(self):
        instance = self.conv("bad", {"foo": "bar"})
        self.assertEqual(instance.foo, "bar")

    def testTwoConversions(self):
        instance1 = self.conv(None, {"foo": "bar"})
        self.assertEqual(instance1.foo, "bar")
        instance2 = self.conv(instance1, {"foo": "baz"})
        self.assertIs(instance2, instance1)
        self.assertEqual(instance2.foo, "baz")

    def testFailedConversion(self):
        with self.assertRaises(rcv._ConversionException):
            self.conv(None, [])


class ClassConverterTestCase(unittest.TestCase):
    class TheClass(object):
        def __init__(self, session, attributes, eTag):
            self.Session = session
            self.__foo = rcv.Attribute("TheClass.foo", rcv.StringConverter, rcv.Absent)
            self._updateAttributes(eTag, **attributes)

        @property
        def foo(self):
            return self.__foo.value

        def _updateAttributes(self, eTag, foo=rcv.Absent, **kwds):
            self.eTag = eTag
            self.__foo.update(foo)

    def setUp(self):
        self.session = object()
        self.conv = rcv.ClassConverter(self.session, self.TheClass)

    def testDescription(self):
        self.assertEqual(self.conv.desc, "TheClass")

    def testConversion(self):
        instance = self.conv(None, {"foo": "bar"})
        self.assertEqual(instance.foo, "bar")
        self.assertIs(instance.Session, self.session)
        self.assertIsNone(instance.eTag)

    def testTwoConversions(self):
        instance1 = self.conv(None, {"foo": "bar"})
        self.assertEqual(instance1.foo, "bar")
        instance2 = self.conv(instance1, {"foo": "baz"})
        self.assertIs(instance2, instance1)
        self.assertEqual(instance2.foo, "baz")


class KeyedStructureUnionConverterTestCase(unittest.TestCase):
    def setUp(self):
        self.mocks = MockMockMock.Engine()
        self.conv1 = self.mocks.create("conv1")
        self.conv2 = self.mocks.create("conv2")
        self.instance1 = self.mocks.create("instance1")
        self.instance2 = self.mocks.create("instance2")
        self.conv = rcv.KeyedStructureUnionConverter(
            "key",
            {
                "val1": self.conv1.object,
                "val2": self.conv2.object,
            }
        )

    def tearDown(self):
        self.mocks.tearDown()

    def testDesc(self):
        with self.mocks.unordered:
            self.conv1.expect.desc.andReturn("desc1")
            self.conv2.expect.desc.andReturn("desc2")
        self.assertEqual(self.conv.desc, "desc1 or desc2")

    def testOneConversion(self):
        ret = object()

        self.conv1.expect(None, {"key": "val1"}).andReturn(ret)

        actual = self.conv(None, {"key": "val1"})
        self.assertIs(actual, ret)

    def testBadKey(self):
        with self.assertRaises(rcv._ConversionException):
            self.conv(None, {"key": "not_a_val"})

    def testNoKey(self):
        with self.assertRaises(rcv._ConversionException):
            self.conv(None, {})

    def testNotADict(self):
        with self.assertRaises(rcv._ConversionException):
            self.conv(None, 42)

    def testTwoConversionsOfSameKey(self):
        ret = object()

        self.conv1.expect(None, {"key": "val1", "foo": "bar"}).andReturn(ret)
        self.conv1.expect(ret, {"key": "val1", "foo": "baz"}).andReturn(ret)

        instance1 = self.conv(None, {"key": "val1", "foo": "bar"})
        instance2 = self.conv(instance1, {"key": "val1", "foo": "baz"})
        self.assertIs(instance1, ret)
        self.assertIs(instance2, ret)

    def testTwoConversionsOfDifferentKeys(self):
        ret1 = object()
        ret2 = object()

        self.conv1.expect(None, {"key": "val1"}).andReturn(ret1)
        self.conv2.expect(ret1, {"key": "val2"}).andReturn(ret2)

        instance1 = self.conv(None, {"key": "val1"})
        instance2 = self.conv(instance1, {"key": "val2"})
        self.assertIs(instance1, ret1)
        self.assertIs(instance2, ret2)


class FirstMatchUnionConverterTestCase(unittest.TestCase):
    def setUp(self):
        self.mocks = MockMockMock.Engine()
        self.conv1 = self.mocks.create("conv1")
        self.conv2 = self.mocks.create("conv2")
        self.instance1 = self.mocks.create("instance1")
        self.instance2 = self.mocks.create("instance2")
        self.conv = rcv.FirstMatchUnionConverter(self.conv1.object, self.conv2.object)

    def tearDown(self):
        self.mocks.tearDown()

    def testDesc(self):
        self.conv1.expect.desc.andReturn("desc1")
        self.conv2.expect.desc.andReturn("desc2")

        self.assertEqual(self.conv.desc, "desc1 or desc2")

    def testFirstConverterMatches(self):
        self.conv1.expect(None, 42).andReturn("42")

        self.assertEqual(self.conv(None, 42), "42")

    def testSecondConverterMatches(self):
        self.conv1.expect(None, 42).andRaise(rcv._ConversionException())
        self.conv2.expect(None, 42).andReturn("forty-two")

        self.assertEqual(self.conv(None, 42), "forty-two")

    def testNoConverterMatches(self):
        self.conv1.expect(None, 42).andRaise(rcv._ConversionException())
        self.conv2.expect(None, 42).andRaise(rcv._ConversionException())

        with self.assertRaises(rcv._ConversionException):
            self.conv(None, 42)


class DictConverterTestCase(unittest.TestCase):
    def setUp(self):
        self.mocks = MockMockMock.Engine()
        self.key = self.mocks.create("key")
        self.value = self.mocks.create("value")
        self.instance1 = self.mocks.create("instance1")
        self.instance2 = self.mocks.create("instance2")
        self.conv = rcv.DictConverter(self.key.object, self.value.object)

    def tearDown(self):
        self.mocks.tearDown()

    def testDesc(self):
        self.key.expect.desc.andReturn("desc1")
        self.value.expect.desc.andReturn("desc2")

        self.assertEqual(self.conv.desc, "dict of desc1 to desc2")

    def testConversion(self):
        self.key.expect(None, 42).andReturn("42")
        self.value.expect(None, "57").andReturn(57)

        self.assertEqual(self.conv(None, {42: "57"}), {"42": 57})

    def testSecondConversionWithSameKey(self):
        self.key.expect(None, 42).andReturn("42")
        self.value.expect(57, "58").andReturn(58)

        instance = {"42": 57}
        ret = self.conv(instance, {42: "58"})
        self.assertEqual(ret, {"42": 58})
        self.assertIs(ret, instance)

    def testSecondConversionWithDifferentKey(self):
        self.key.expect(None, 43).andReturn("43")
        self.value.expect(None, "58").andReturn(58)

        instance = {"42": 57}
        ret = self.conv(instance, {43: "58"})
        self.assertEqual(ret, {"43": 58})
        self.assertIs(ret, instance)

    def testSecondConversionWithSeveralKeys(self):
        with self.mocks.unordered:
            with self.mocks.ordered:
                self.key.expect(None, 42).andReturn("42")
                self.value.expect(57, "47").andReturn(47)
            with self.mocks.ordered:
                self.key.expect(None, 44).andReturn("44")
                self.value.expect(None, "59").andReturn(59)

        instance = {"42": 57, "43": 58}
        ret = self.conv(instance, {42: "47", 44: "59"})
        self.assertEqual(ret, {"42": 47, "44": 59})
        self.assertIs(ret, instance)

    def testBadConversion(self):
        with self.assertRaises(rcv._ConversionException):
            self.conv(None, [])


class PaginatedListConverterTestCase(unittest.TestCase):
    def setUp(self):
        self.mocks = MockMockMock.Engine()
        self.session = (42, )
        self.content = self.mocks.create("content")
        self.request = self.mocks.create("request")
        self.conv = rcv.PaginatedListConverter(self.session, self.content.object)

    def tearDown(self):
        self.mocks.tearDown()

    def testDesc(self):
        self.content.expect.desc.andReturn("desc")

        self.assertEqual(self.conv.desc, "PaginatedList of desc")

    def testCall(self):
        self.request.expect.json().andReturn([])

        l = self.conv(None, self.request.object)
        self.assertIsInstance(l, pgl.PaginatedList)


class FileDirSubmoduleSymLinkUnionConverterTestCase(unittest.TestCase):
    def setUp(self):
        self.mocks = MockMockMock.Engine()
        self.file = self.mocks.create("file")
        self.dir = self.mocks.create("dir")
        self.submodule = self.mocks.create("submodule")
        self.symlink = self.mocks.create("symlink")
        self.conv = rcv.FileDirSubmoduleSymLinkUnionConverter(self.file.object, self.dir.object, self.submodule.object, self.symlink.object)

    def tearDown(self):
        self.mocks.tearDown()

    def testDesc(self):
        self.file.expect.desc.andReturn("file")
        self.dir.expect.desc.andReturn("dir")
        self.submodule.expect.desc.andReturn("submodule")
        self.symlink.expect.desc.andReturn("symlink")

        self.assertEqual(self.conv.desc, "file or dir or submodule or symlink")

    def testBadConversion(self):
        with self.assertRaises(rcv._ConversionException):
            self.conv(None, [])

    def testEmptyDict(self):
        with self.assertRaises(rcv._ConversionException):
            self.conv(None, {})

    def testBadType(self):
        with self.assertRaises(rcv._ConversionException):
            self.conv(None, {"type": "foo"})

    def testFile(self):
        self.file.expect(None, {"type": "file"}).andReturn(42)

        self.assertEqual(self.conv(None, {"type": "file"}), 42)

    def testDir(self):
        self.dir.expect(None, {"type": "dir"}).andReturn(42)

        self.assertEqual(self.conv(None, {"type": "dir"}), 42)

    def testSymlink(self):
        self.symlink.expect(None, {"type": "symlink"}).andReturn(42)

        self.assertEqual(self.conv(None, {"type": "symlink"}), 42)

    def testSubmodule(self):
        self.submodule.expect(None, {"type": "file", "git_url": "foo/git/trees/xxx"}).andReturn(42)

        self.assertEqual(self.conv(None, {"type": "file", "git_url": "foo/git/trees/xxx"}), 42)

    def testSubmoduleWithoutDotGitmodules(self):
        self.submodule.expect(None, {"type": "file", "git_url": None}).andReturn(42)

        self.assertEqual(self.conv(None, {"type": "file", "git_url": None}), 42)


class BuiltinReturnValueTestCase(unittest.TestCase):
    def testIntegerReturnValueDescription(self):
        self.assertEqual(rcv.IntReturnValue.desc, "Integral")

    def testIntegerConversion(self):
        self.assertEqual(rcv.IntReturnValue(42), 42)

    def testLongConversion(self):
        self.assertEqual(rcv.IntReturnValue(999999999999), 999999999999)

    def testBadIntegerConversion(self):
        with self.assertRaises(rcv._ReturnValueException):
            rcv.IntReturnValue("42")

    def testStringReturnValueDescription(self):
        self.assertEqual(rcv.StringReturnValue.desc, stringName)

    def testStringConversion(self):
        self.assertEqual(rcv.StringReturnValue("42"), "42")

    def testBadStringConversion(self):
        with self.assertRaises(rcv._ReturnValueException):
            rcv.StringReturnValue(42)

    def testDatetimeReturnValueDescription(self):
        self.assertEqual(rcv.DatetimeReturnValue.desc, "datetime")

    def testDatetimeConversionFromInt(self):
        self.assertEqual(rcv.DatetimeReturnValue(1395971262), datetime.datetime(2014, 3, 28, 1, 47, 42))

    def testDatetimeConversionFromString(self):
        self.assertEqual(rcv.DatetimeReturnValue("2010-07-09T06:10:06Z"), datetime.datetime(2010, 7, 9, 6, 10, 6))

    def testBadDatetimeConversion(self):
        with self.assertRaises(rcv._ReturnValueException):
            rcv.DatetimeReturnValue(4.5)

    def testBadDatetimeConversionFromString(self):
        with self.assertRaises(rcv._ReturnValueException):
            rcv.DatetimeReturnValue("foobar")


class ListReturnValueTestCase(unittest.TestCase):
    def setUp(self):
        self.mocks = MockMockMock.Engine()
        self.content = self.mocks.create("content")
        self.conv = rcv.ListReturnValue(self.content.object)

    def tearDown(self):
        self.mocks.tearDown()

    def testDescription(self):
        self.content.expect.desc.andReturn("desc")
        self.assertEqual(self.conv.desc, "list of desc")

    def testGoodConversion(self):
        self.content.expect(42, None).andReturn("42")
        self.content.expect(43, None).andReturn("43")

        self.assertEqual(self.conv([42, 43]), ["42", "43"])

    def testNotAList(self):
        with self.assertRaises(rcv._ReturnValueException):
            self.conv(42)

    def testBadElement(self):
        self.content.expect(42, None).andReturn("42")
        self.content.expect(43, None).andRaise(rcv._ReturnValueException())

        with self.assertRaises(rcv._ReturnValueException):
            self.conv([42, 43, 44])


class StructureReturnValueTestCase(unittest.TestCase):
    class TheStruct(object):
        def __init__(self, session, attributes):
            self.Session = session
            self.__foo = rcv.Attribute("TheStruct.foo", rcv.StringConverter, rcv.Absent)
            self._updateAttributes(**attributes)

        @property
        def foo(self):
            return self.__foo.value

        def _updateAttributes(self, foo=rcv.Absent, **kwds):
            self.__foo.update(foo)

    def setUp(self):
        self.session = object()
        self.conv = rcv.StructureReturnValue(self.session, self.TheStruct)

    def testDescription(self):
        self.assertEqual(self.conv.desc, "TheStruct")

    def testConversion(self):
        instance = self.conv({"foo": "bar"})
        self.assertEqual(instance.foo, "bar")
        self.assertIs(instance.Session, self.session)

    def testConversionFromEmptyDict(self):
        instance = self.conv({})
        self.assertEqual(instance.foo, None)

    def testConversionWithUnexpectedKeys(self):
        instance = self.conv({"toto": "tutu"})
        self.assertEqual(instance.foo, None)

    def testFailedConversion(self):
        with self.assertRaises(rcv._ReturnValueException):
            self.conv([])


class ClassReturnValueTestCase(unittest.TestCase):
    class TheClass(object):
        def __init__(self, session, attributes, eTag):
            self.Session = session
            self.__foo = rcv.Attribute("TheClass.foo", rcv.StringConverter, rcv.Absent)
            self._updateAttributes(eTag, **attributes)

        @property
        def foo(self):
            return self.__foo.value

        def _updateAttributes(self, eTag, foo=rcv.Absent, **kwds):
            self.eTag = eTag
            self.__foo.update(foo)

    def setUp(self):
        self.session = object()
        self.conv = rcv.ClassReturnValue(self.session, self.TheClass)

    def testDescription(self):
        self.assertEqual(self.conv.desc, "TheClass")

    def testConversion(self):
        instance = self.conv({"foo": "bar"})
        self.assertEqual(instance.foo, "bar")
        self.assertIs(instance.Session, self.session)
        self.assertIsNone(instance.eTag)

    def testConversionWithEtag(self):
        instance = self.conv({"foo": "bar"}, 42)
        self.assertEqual(instance.foo, "bar")
        self.assertIs(instance.Session, self.session)
        self.assertEqual(instance.eTag, 42)


class KeyedStructureUnionReturnValueTestCase(unittest.TestCase):
    def setUp(self):
        self.mocks = MockMockMock.Engine()
        self.conv1 = self.mocks.create("conv1")
        self.conv2 = self.mocks.create("conv2")
        self.instance1 = self.mocks.create("instance1")
        self.instance2 = self.mocks.create("instance2")
        self.conv = rcv.KeyedStructureUnionReturnValue(
            "key",
            {
                "val1": self.conv1.object,
                "val2": self.conv2.object,
            }
        )

    def tearDown(self):
        self.mocks.tearDown()

    def testDesc(self):
        with self.mocks.unordered:
            self.conv1.expect.desc.andReturn("desc1")
            self.conv2.expect.desc.andReturn("desc2")
        self.assertEqual(self.conv.desc, "desc1 or desc2")

    def testConversion(self):
        ret = object()

        self.conv1.expect({"key": "val1"}, "etag").andReturn(ret)

        actual = self.conv({"key": "val1"}, "etag")
        self.assertIs(actual, ret)

    def testBadKey(self):
        with self.assertRaises(rcv._ReturnValueException):
            self.conv({"key": "not_a_val"})

    def testNoKey(self):
        with self.assertRaises(rcv._ReturnValueException):
            self.conv({})

    def testNotADict(self):
        with self.assertRaises(rcv._ReturnValueException):
            self.conv(42)


class FirstMatchUnionReturnValueTestCase(unittest.TestCase):
    def setUp(self):
        self.mocks = MockMockMock.Engine()
        self.conv1 = self.mocks.create("conv1")
        self.conv2 = self.mocks.create("conv2")
        self.instance1 = self.mocks.create("instance1")
        self.instance2 = self.mocks.create("instance2")
        self.conv = rcv.FirstMatchUnionReturnValue(self.conv1.object, self.conv2.object)

    def tearDown(self):
        self.mocks.tearDown()

    def testDesc(self):
        self.conv1.expect.desc.andReturn("desc1")
        self.conv2.expect.desc.andReturn("desc2")

        self.assertEqual(self.conv.desc, "desc1 or desc2")

    def testFirstReturnValueMatches(self):
        self.conv1.expect(42, "etag").andReturn("42")

        self.assertEqual(self.conv(42, "etag"), "42")

    def testSecondReturnValueMatches(self):
        self.conv1.expect(42, "etag").andRaise(rcv._ReturnValueException())
        self.conv2.expect(42, "etag").andReturn("forty-two")

        self.assertEqual(self.conv(42, "etag"), "forty-two")

    def testNoReturnValueMatches(self):
        self.conv1.expect(42, "etag").andRaise(rcv._ReturnValueException())
        self.conv2.expect(42, "etag").andRaise(rcv._ReturnValueException())

        with self.assertRaises(rcv._ReturnValueException):
            self.conv(42, "etag")


class DictReturnValueTestCase(unittest.TestCase):
    def setUp(self):
        self.mocks = MockMockMock.Engine()
        self.key = self.mocks.create("key")
        self.value = self.mocks.create("value")
        self.instance1 = self.mocks.create("instance1")
        self.instance2 = self.mocks.create("instance2")
        self.conv = rcv.DictReturnValue(self.key.object, self.value.object)

    def tearDown(self):
        self.mocks.tearDown()

    def testDesc(self):
        self.key.expect.desc.andReturn("desc1")
        self.value.expect.desc.andReturn("desc2")

        self.assertEqual(self.conv.desc, "dict of desc1 to desc2")

    def testConversion(self):
        self.key.expect(42, None).andReturn("42")
        self.value.expect("57", None).andReturn(57)

        self.assertEqual(self.conv({42: "57"}), {"42": 57})

    def testBadConversion(self):
        with self.assertRaises(rcv._ReturnValueException):
            self.conv([])


class PaginatedListReturnValueTestCase(unittest.TestCase):
    def setUp(self):
        self.mocks = MockMockMock.Engine()
        self.session = object()
        self.content = self.mocks.create("content")
        self.request = self.mocks.create("request")
        self.conv = rcv.PaginatedListReturnValue(self.session, self.content.object)

    def tearDown(self):
        self.mocks.tearDown()

    def testDesc(self):
        self.content.expect.desc.andReturn("desc")

        self.assertEqual(self.conv.desc, "PaginatedList of desc")

    def testCall(self):
        self.request.expect.json().andReturn([])

        l = self.conv(self.request.object)
        self.assertIsInstance(l, pgl.PaginatedList)


class FileDirSubmoduleSymLinkUnionReturnValueTestCase(unittest.TestCase):
    def setUp(self):
        self.mocks = MockMockMock.Engine()
        self.file = self.mocks.create("file")
        self.dir = self.mocks.create("dir")
        self.submodule = self.mocks.create("submodule")
        self.symlink = self.mocks.create("symlink")
        self.conv = rcv.FileDirSubmoduleSymLinkUnionReturnValue(self.file.object, self.dir.object, self.submodule.object, self.symlink.object)

    def tearDown(self):
        self.mocks.tearDown()

    def testDesc(self):
        self.file.expect.desc.andReturn("file")
        self.dir.expect.desc.andReturn("dir")
        self.submodule.expect.desc.andReturn("submodule")
        self.symlink.expect.desc.andReturn("symlink")

        self.assertEqual(self.conv.desc, "file or dir or submodule or symlink")

    def testBadConversion(self):
        with self.assertRaises(rcv._ReturnValueException):
            self.conv([], "etag")

    def testEmptyDict(self):
        with self.assertRaises(rcv._ReturnValueException):
            self.conv({}, "etag")

    def testBadType(self):
        with self.assertRaises(rcv._ReturnValueException):
            self.conv({"type": "foo"}, "etag")

    def testFile(self):
        self.file.expect({"type": "file"}, "etag").andReturn(42)

        self.assertEqual(self.conv({"type": "file"}, "etag"), 42)

    def testDir(self):
        self.dir.expect({"type": "dir"}, "etag").andReturn(42)

        self.assertEqual(self.conv({"type": "dir"}, "etag"), 42)

    def testSymlink(self):
        self.symlink.expect({"type": "symlink"}, "etag").andReturn(42)

        self.assertEqual(self.conv({"type": "symlink"}, "etag"), 42)

    def testSubmodule(self):
        self.submodule.expect({"type": "file", "git_url": "foo/git/trees/xxx"}, "etag").andReturn(42)

        self.assertEqual(self.conv({"type": "file", "git_url": "foo/git/trees/xxx"}, "etag"), 42)

    def testSubmoduleWithoutDotGitmodules(self):
        self.submodule.expect({"type": "file", "git_url": None}, "etag").andReturn(42)

        self.assertEqual(self.conv({"type": "file", "git_url": None}, "etag"), 42)

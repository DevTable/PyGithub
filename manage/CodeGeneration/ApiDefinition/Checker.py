# -*- coding: utf-8 -*-

# Copyright 2013-2014 Vincent Jacques <vincent@vincent-jacques.net>

import sys
assert sys.hexversion >= 0x03040000

import itertools
import unittest

import CodeGeneration.ApiDefinition.CrossReferenced as CrossReferenced
import CodeGeneration.ApiDefinition.Structured as Structured

# @todoAlpha Detect classes/structures with the same attributes (GitCommit.Author and GitTag.Tagger)


class Checker(object):
    def __init__(self, definition):
        self.definition = definition

    def check(self, *acknowledgedWarnings):  # pragma no cover
        acknowledgedWarnings = set(acknowledgedWarnings)
        for w in self.warnings():
            if w in acknowledgedWarnings:
                acknowledgedWarnings.remove(w)
            else:
                print("WARNING:", w)
        for w in acknowledgedWarnings:
            print("WARNING: \"", w, "\" was acknowledged but doesn't exist anymore")

    def warnings(self):
        yield from ("Struct '{}' is not updatable but is the type of attribute '{}'".format(s.qualifiedName, a.qualifiedName) for (c, s, a) in self.notUpdatableStructuresAttributeOfClass())
        yield from ("End-point '{} {}' is not implemented and not declared so".format(ep.verb, ep.url) for ep in self.unimplementedEndPointsNotDeclared())
        yield from ("End-point '{} {}' is declared as not implemented but is implemented by '{}'".format(ep.verb, ep.url, m.qualifiedName) for (ep, m) in self.implementedEndPointsDeclaredUnimplemented())
        yield from ("Method '{}' doesn't use its '{}' parameter".format(m.qualifiedName, p.name) for (m, p) in self.unusedParameters())  # @todoAlpha Add a method attribute to Parameter
        yield from ("Method '{}' doesn't implement the '{}' parameter of the '{} {}' end-point".format(m.qualifiedName, p, ep.verb, ep.url) for (m, ep, p) in self.unimplementedEndPointParametersNotDeclared())
        yield from ("In method '{}', the '{}' parameter of the '{} {}' end-point is declared as not implemented but is implemented".format(m.qualifiedName, p, ep.verb, ep.url) for (m, ep, p) in self.implementedEndPointParametersDeclaredUnimplemented())
        yield from ("Method '{}' tries to use unexisting parameter '{}'".format(m.qualifiedName, p) for (m, p) in self.unexistingParameters())
        yield from ("Method '{}' re-orders the '{} {}' parameters ('{}') to ('{}')".format(m.qualifiedName, ep.verb, ep.url, "', '".join(ep.parameters), "', '".join(p.name for p in m.parameters)) for (m, ep) in self.reorderedParameters())
        yield from ("Attribute '{}' hides attribute '{}'".format(v.qualifiedName, h.qualifiedName) for (v, h) in self.hiddenAttributes())
        yield from ("Method '{}' hides method '{}'".format(v.qualifiedName, h.qualifiedName) for (v, h) in self.hiddenMethods())
        yield from ("Class '{}' inherits method '{}' and has methods".format(c.qualifiedName, m.qualifiedName) for (c, m) in self.inheritedMethods())
        yield from ("Attribute '{}' is not used as an end point".format(a.qualifiedName) for a in self.unusedUrlAttributes())

    def notUpdatableStructuresAttributeOfClass(self):
        for c1 in self.definition.classes:
            for s in c1.structures:
                if not s.isUpdatable:
                    for c2 in self.definition.classes:
                        for a in c2.attributes:
                            if a.type.qualifiedName == s.qualifiedName:
                                yield c2, s, a

    def unimplementedEndPointsNotDeclared(self):
        unimplemented = set(self.definition.endPoints) - set(ep for ep, reason in self.definition.unimplementedEndPoints)
        for c in self.definition.classes:
            for m in c.methods:
                for ep in m.endPoints:
                    unimplemented.discard(ep)
        return unimplemented

    def implementedEndPointsDeclaredUnimplemented(self):
        unimplemented = set(ep for ep, reason in self.definition.unimplementedEndPoints)
        for c in self.definition.classes:
            for m in c.methods:
                for ep in m.endPoints:
                    if ep in unimplemented:
                        yield ep, m

    def unusedParameters(self):
        for c in self.definition.classes:
            for m in c.methods:
                for p in m.parameters:
                    for a in itertools.chain(m.urlTemplateArguments, m.urlArguments, m.postArguments, m.headers):
                        if isinstance(a.value, CrossReferenced.ParameterValue) and a.value.parameter == p.name:
                            break
                        if isinstance(a.value, CrossReferenced.RepositoryOwnerValue) and a.value.repository == p.name:
                            break
                        if isinstance(a.value, CrossReferenced.RepositoryNameValue) and a.value.repository == p.name:
                            break
                    else:
                        yield m, p

    def unimplementedEndPointParametersNotDeclared(self):
        for c in self.definition.classes:
            for m in c.methods:
                for ep in m.endPoints:
                    unimplemented = set(ep.parameters) - set(m.unimplementedParameters)
                    for p in m.parameters:
                        unimplemented.discard(p.name)
                    for p in unimplemented:
                        yield m, ep, p

    def implementedEndPointParametersDeclaredUnimplemented(self):
        for c in self.definition.classes:
            for m in c.methods:
                for ep in m.endPoints:
                    unimplemented = set(m.unimplementedParameters)
                    for p in m.parameters:
                        if p.name in unimplemented:
                            yield m, ep, p.name

    def unexistingParameters(self):
        for c in self.definition.classes:
            for m in c.methods:
                for a in itertools.chain(m.urlTemplateArguments, m.urlArguments, m.postArguments):
                    if isinstance(a.value, CrossReferenced.ParameterValue):
                        for p in m.parameters:
                            if p.name == a.value.parameter:
                                break
                        else:
                            yield m, a.value.parameter

    def reorderedParameters(self):
        for c in self.definition.classes:
            for m in c.methods:
                for ep in m.endPoints:
                    methodParams = [p.name for p in m.parameters if p.name in ep.parameters]
                    epParams = [p for p in ep.parameters if p in methodParams]
                    if methodParams != epParams:
                        yield m, ep

    def hiddenAttributes(self):
        def gatherAttributes(c):
            if c is None:
                return dict()
            else:
                attributes = gatherAttributes(c.base)
                attributes.update({a.simpleName: a for a in c.attributes})
                return attributes

        for c in self.definition.classes:
            baseAttributes = gatherAttributes(c.base)
            for a in c.attributes:
                if a.simpleName in baseAttributes:
                    yield a, baseAttributes[a.simpleName]

    def hiddenMethods(self):
        def gatherMethods(c):
            if c is None:
                return dict()
            else:
                methods = gatherMethods(c.base)
                methods.update({m.simpleName: m for m in c.methods})
                return methods

        for c in self.definition.classes:
            baseMethods = gatherMethods(c.base)
            for m in c.methods:
                if m.simpleName in baseMethods:
                    yield m, baseMethods[m.simpleName]

    def unusedUrlAttributes(self):
        # @todoAlpha Do the same for structures
        for c in self.definition.classes:
            usedAsEndpoints = set()
            for m in c.methods:
                if isinstance(m.urlTemplate, CrossReferenced.AttributeValue):
                    usedAsEndpoints.add(m.urlTemplate.attribute)
            for a in c.attributes:
                if a.simpleName.endswith("_url") and a.simpleName not in usedAsEndpoints:
                    yield a

    def inheritedMethods(self):
        def gatherMethods(c):
            if c is None:
                return []
            else:
                yield from gatherMethods(c.base)
                yield from c.methods

        for c in self.definition.classes:
            if len(c.methods) != 0:
                for m in gatherMethods(c.base):
                    yield c, m


class CheckerTestCase(unittest.TestCase):
    def expect(self, d, *warnings):
        typesRepo = CrossReferenced.TypesRepository()
        typesRepo.register(CrossReferenced.BuiltinType("string"))
        self.assertEqual(set(Checker(CrossReferenced.Definition(d, typesRepo)).warnings()), set(warnings))

    def testNotUpdatableStructureIsAttributeOfClass(self):
        d = Structured.Definition(
            (),
            (
                Structured.Class("Foo", None, (Structured.Structure("Stru", False, (), ()),), (Structured.Attribute("url", Structured.ScalarType("string")), Structured.Attribute("attr", Structured.ScalarType("Foo.Stru"))), (), ()),
            ),
            ()
        )
        self.expect(d, "Struct 'Foo.Stru' is not updatable but is the type of attribute 'Foo.attr'")

    def testUnimplementedEndPointNotDeclared(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (),
            ()
        )
        self.expect(d, "End-point 'GET /foo' is not implemented and not declared so")

    def testUnimplementedEndPointDeclared(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/bar", (), ""),
            ),
            (),
            (("family", (Structured.UnimplementedStuff("GET /bar", None),)),)
        )
        self.expect(d)

    def testImplementedEndPoint(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (), (), Structured.EndPointValue(), (), (), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testImplementedEndPointDeclaredAsUnimplemented(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (), (), Structured.EndPointValue(), (), (), (), (), (), None, Structured.NoneType),), ()),
            ),
            (("family", (Structured.UnimplementedStuff("GET /foo", None),)),)
        )
        self.expect(d, "End-point 'GET /foo' is declared as not implemented but is implemented by 'Bar.get_foo'")

    def testUnusedParameter(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("bar", Structured.ScalarType("string"), False, False),), (), Structured.EndPointValue(), (), (), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d, "Method 'Bar.get_foo' doesn't use its 'bar' parameter")

    def testParameterUsedAsUrlTemplateArgument(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("bar", Structured.ScalarType("string"), False, False),), (), Structured.EndPointValue(), (Structured.Argument("baz", Structured.ParameterValue("bar",)),), (), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testParameterUsedAsUrlArgument(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("bar", Structured.ScalarType("string"), False, False),), (), Structured.EndPointValue(), (), (Structured.Argument("baz", Structured.ParameterValue("bar",)),), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testParameterUsedAsPostArgument(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("bar", Structured.ScalarType("string"), False, False),), (), Structured.EndPointValue(), (), (), (Structured.Argument("baz", Structured.ParameterValue("bar",)),), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testParameterUsedAsHeader(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("bar", Structured.ScalarType("string"), False, False),), (), Structured.EndPointValue(), (), (), (), (Structured.Argument("baz", Structured.ParameterValue("bar",)),), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testParameterUsedAsRepoOwnerInUrlTemplateArgument(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("bar", Structured.ScalarType("string"), False, False),), (), Structured.EndPointValue(), (Structured.Argument("baz", Structured.RepositoryOwnerValue("bar",)),), (), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testParameterUsedAsRepoOwnerInUrlArgument(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("bar", Structured.ScalarType("string"), False, False),), (), Structured.EndPointValue(), (), (Structured.Argument("baz", Structured.RepositoryOwnerValue("bar",)),), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testParameterUsedAsRepoOwnerInPostArgument(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("bar", Structured.ScalarType("string"), False, False),), (), Structured.EndPointValue(), (), (), (Structured.Argument("baz", Structured.RepositoryOwnerValue("bar",)),), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testParameterUsedAsRepoNameInUrlTemplateArgument(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("bar", Structured.ScalarType("string"), False, False),), (), Structured.EndPointValue(), (Structured.Argument("baz", Structured.RepositoryNameValue("bar",)),), (), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testParameterUsedAsRepoNameInUrlArgument(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("bar", Structured.ScalarType("string"), False, False),), (), Structured.EndPointValue(), (), (Structured.Argument("baz", Structured.RepositoryNameValue("bar",)),), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testParameterUsedAsRepoNameInPostArgument(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("bar", Structured.ScalarType("string"), False, False),), (), Structured.EndPointValue(), (), (), (Structured.Argument("baz", Structured.RepositoryNameValue("bar",)),), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testUnimplementedEndPointParameterNotDeclared(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", ("bar",), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (), (), Structured.EndPointValue(), (), (), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d, "Method 'Bar.get_foo' doesn't implement the 'bar' parameter of the 'GET /foo' end-point")

    def testUnimplementedEndPointParameterDeclared(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", ("bar",), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (), (Structured.UnimplementedStuff("bar", "reason"),), Structured.EndPointValue(), (), (), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testImplementedEndPointParameterDeclaredAsUnimplemented(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", ("bar",), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("bar", Structured.ScalarType("string"), False, False),), (Structured.UnimplementedStuff("bar", "reason"),), Structured.EndPointValue(), (), (Structured.Argument("baz", Structured.ParameterValue("bar",)),), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d, "In method 'Bar.get_foo', the 'bar' parameter of the 'GET /foo' end-point is declared as not implemented but is implemented")

    def testImplementedEndPointParameter(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", ("bar",), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("bar", Structured.ScalarType("string"), False, False),), (), Structured.EndPointValue(), (), (Structured.Argument("baz", Structured.ParameterValue("bar",)),), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testOderedEndPointParameter(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", ("c", "a", "b"), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("c", Structured.ScalarType("string"), False, False), Structured.Parameter("b", Structured.ScalarType("string"), False, False)), (Structured.UnimplementedStuff("a", "reason"),), Structured.EndPointValue(), (), (Structured.Argument("baz", Structured.ParameterValue("b")), Structured.Argument("foo", Structured.ParameterValue("c"))), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testUnoderedEndPointParameter(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", ("c", "a", "b"), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (Structured.Parameter("b", Structured.ScalarType("string"), False, False), Structured.Parameter("c", Structured.ScalarType("string"), False, False)), (Structured.UnimplementedStuff("a", "reason"),), Structured.EndPointValue(), (), (Structured.Argument("baz", Structured.ParameterValue("b")), Structured.Argument("foo", Structured.ParameterValue("c"))), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d, "Method 'Bar.get_foo' re-orders the 'GET /foo' parameters ('c', 'a', 'b') to ('b', 'c')")

    def testUnexistingParameterUsedAsUrlTemplateArgument(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (), (), Structured.EndPointValue(), (Structured.Argument("baz", Structured.ParameterValue("bar",)),), (), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d, "Method 'Bar.get_foo' tries to use unexisting parameter 'bar'")

    def testUnexistingParameterUsedAsUrlArgument(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (), (), Structured.EndPointValue(), (), (Structured.Argument("baz", Structured.ParameterValue("bar",)),), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d, "Method 'Bar.get_foo' tries to use unexisting parameter 'bar'")

    def testUnexistingParameterUsedAsPostArgument(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Bar", None, (), (Structured.Attribute("url", Structured.ScalarType("string")),), (Structured.Method("get_foo", ("GET /foo",), (), (), Structured.EndPointValue(), (), (), (Structured.Argument("baz", Structured.ParameterValue("bar",)),), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d, "Method 'Bar.get_foo' tries to use unexisting parameter 'bar'")

    def testAttributeHidesAttributeOfBase(self):
        d = Structured.Definition(
            (),
            (
                Structured.Class("Foo", None, (), (Structured.Attribute("slug", Structured.ScalarType("string")),), (), ()),
                Structured.Class("Bar", Structured.ScalarType("Foo"), (), (Structured.Attribute("slug", Structured.ScalarType("string")),), (), ()),
            ),
            ()
        )
        self.expect(d, "Attribute 'Bar.slug' hides attribute 'Foo.slug'")

    def testAttributeHidesAttributeOfIndirectBase(self):
        d = Structured.Definition(
            (),
            (
                Structured.Class("Foo", None, (), (Structured.Attribute("slug", Structured.ScalarType("string")),), (), ()),
                Structured.Class("Bar", Structured.ScalarType("Foo"), (), (), (), ()),
                Structured.Class("Baz", Structured.ScalarType("Bar"), (), (Structured.Attribute("slug", Structured.ScalarType("string")),), (), ()),
            ),
            ()
        )
        self.expect(d, "Attribute 'Baz.slug' hides attribute 'Foo.slug'")

    def testMethodHidesMethodOfBase(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Foo", None, (), (), (Structured.Method("get_foo", ("GET /foo",), (), (), Structured.EndPointValue(), (), (), (), (), (), None, Structured.NoneType),), ()),
                Structured.Class("Bar", Structured.ScalarType("Foo"), (), (), (Structured.Method("get_foo", ("GET /foo",), (), (), Structured.EndPointValue(), (), (), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d, "Method 'Bar.get_foo' hides method 'Foo.get_foo'", "Class 'Bar' inherits method 'Foo.get_foo' and has methods")

    def testMethodHidesMethodOfIndirectBase(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Foo", None, (), (), (Structured.Method("get_foo", ("GET /foo",), (), (), Structured.EndPointValue(), (), (), (), (), (), None, Structured.NoneType),), ()),
                Structured.Class("Bar", Structured.ScalarType("Foo"), (), (), (), ()),
                Structured.Class("Baz", Structured.ScalarType("Bar"), (), (), (Structured.Method("get_foo", ("GET /foo",), (), (), Structured.EndPointValue(), (), (), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d, "Method 'Baz.get_foo' hides method 'Foo.get_foo'", "Class 'Baz' inherits method 'Foo.get_foo' and has methods")

    def testUrlAttributeNotUsed(self):
        d = Structured.Definition(
            (),
            (
                Structured.Class("Foo", None, (), (Structured.Attribute("slug_url", Structured.ScalarType("string")),), (), ()),
            ),
            ()
        )
        self.expect(d, "Attribute 'Foo.slug_url' is not used as an end point")

    def testUrlAttributeUsed(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/slug", (), ""),
            ),
            (
                Structured.Class("Foo", None, (), (Structured.Attribute("slug_url", Structured.ScalarType("string")),), (Structured.Method("get_slug", ("GET /slug",), (), (), Structured.AttributeValue("slug_url"), (), (), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d)

    def testClassWithMethodsInheritsMethod(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Foo", None, (), (), (Structured.Method("get_foo", ("GET /foo",), (), (), Structured.EndPointValue(), (), (), (), (), (), None, Structured.NoneType),), ()),
                Structured.Class("Bar", Structured.ScalarType("Foo"), (), (), (Structured.Method("get_bar", ("GET /foo",), (), (), Structured.EndPointValue(), (), (), (), (), (), None, Structured.NoneType),), ()),
            ),
            ()
        )
        self.expect(d, "Class 'Bar' inherits method 'Foo.get_foo' and has methods")

    def testClassWithoutMethodsInheritsMethod(self):
        d = Structured.Definition(
            (
                Structured.EndPoint("GET", "/foo", (), ""),
            ),
            (
                Structured.Class("Foo", None, (), (), (Structured.Method("get_foo", ("GET /foo",), (), (), Structured.EndPointValue(), (), (), (), (), (), None, Structured.NoneType),), ()),
                Structured.Class("Bar", Structured.ScalarType("Foo"), (), (), (), ()),
            ),
            ()
        )
        self.expect(d)

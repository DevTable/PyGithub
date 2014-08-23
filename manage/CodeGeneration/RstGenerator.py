# -*- coding: utf-8 -*-

# Copyright 2013-2014 Vincent Jacques <vincent@vincent-jacques.net>

# @todoAlpha Extract the sha of the commit of the doc, put it in the README and in the doc.

import sys
assert sys.hexversion >= 0x03040000


class RstGenerator:
    def generateApis(self, endPoints, unimplementedEndPoints):
        yield "From Github API v3 to PyGithub"
        yield "=============================="
        yield ""
        yield "Here are the {} end points I'm aware of, and if/where they are implemented in PyGithub.".format(len(endPoints))
        yield "{} end points are not yet implemented, and I don't plan to implement {} end points for reasons described below.".format(len(list(e for e, reason in unimplementedEndPoints.items() if reason is None)), len(list(e for e, reason in unimplementedEndPoints.items() if reason is not None)))
        yield "If something is not listed here, please `open an issue <http://github.com/jacquev6/PyGithub/issues>`__ with a link to the corresponding documentation of Github API v3."
        yield ""
        for endPoint in endPoints:
            title = endPoint.verb + " " + endPoint.url
            yield title
            yield "-" * len(title)
            yield ""
            yield "(`Reference documentation of Github API v3 <{}>`__)".format(endPoint.doc)
            yield ""
            if len(endPoint.methods) != 0:
                yield "Implemented in PyGithub by:"
                for method in endPoint.methods:
                    yield "  * :meth:`.{}`".format(method.qualifiedName)
            elif unimplementedEndPoints[title] is not None:
                yield "Not implemented in PyGithub: " + unimplementedEndPoints[title]
            else:
                yield "Not yet implemented in PyGithub."
            yield ""

    def generateClass(self, klass):
        yield klass.simpleName
        yield "=" * len(klass.simpleName)
        yield ""
        yield ".. automodule:: PyGithub.Blocking.{}".format(klass.simpleName)
        yield ""
        yield ".. autoclass:: PyGithub.Blocking.{0}::{0}()".format(klass.simpleName)
        yield "    :members:"
        if len(klass.structures) != 0:
            yield "    :exclude-members: {}".format(", ".join(struct.simpleName for struct in klass.structures))  # pragma no branch
            yield ""
            for struct in klass.structures:
                yield "    .. autoclass:: PyGithub.Blocking.{}::{}()".format(klass.simpleName, struct.qualifiedName)
                yield "        :members:"

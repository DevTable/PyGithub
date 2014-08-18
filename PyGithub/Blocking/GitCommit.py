# -*- coding: utf-8 -*-

# Copyright 2013-2014 Vincent Jacques <vincent@vincent-jacques.net>

# ######################################################################
# #### This file is generated. Manual changes will likely be lost. #####
# ######################################################################

import uritemplate

import PyGithub.Blocking._base_github_object as _bgo
import PyGithub.Blocking._send as _snd
import PyGithub.Blocking._receive as _rcv


class GitCommit(_bgo.UpdatableGithubObject):
    """
    Base class: :class:`.UpdatableGithubObject`

    Derived classes: none.

    Methods and attributes returning instances of this class:
      * :attr:`.Commit.commit`
      * :meth:`.File.delete`
      * :meth:`.File.edit`
      * :attr:`.GitCommit.parents`
      * :attr:`.GitRef.object`
      * :attr:`.GitTag.object`
      * :attr:`.Repository.ContentCommit.commit`
      * :meth:`.Repository.create_git_commit`
      * :meth:`.Repository.get_git_commit`

    Methods accepting instances of this class as parameter:
      * :meth:`.Repository.create_git_commit`
    """

    class Author(_bgo.SessionedGithubObject):
        """
        Methods and attributes returning instances of this class:
          * :attr:`.GitCommit.author`
          * :attr:`.GitCommit.committer`
          * :attr:`.GitTag.tagger`

        Methods accepting instances of this class as parameter: none.
        """

        def _initAttributes(self, date=None, email=None, name=None, **kwds):
            super(GitCommit.Author, self)._initAttributes(**kwds)
            self.__date = _rcv.Attribute("GitCommit.Author.date", _rcv.DatetimeConverter, date)
            self.__email = _rcv.Attribute("GitCommit.Author.email", _rcv.StringConverter, email)
            self.__name = _rcv.Attribute("GitCommit.Author.name", _rcv.StringConverter, name)

        def _updateAttributes(self, date=None, email=None, name=None, **kwds):
            super(GitCommit.Author, self)._updateAttributes(**kwds)
            self.__date.update(date)
            self.__email.update(email)
            self.__name.update(name)

        @property
        def date(self):
            """
            :type: :class:`datetime`
            """
            return self.__date.value

        @property
        def email(self):
            """
            :type: :class:`string`
            """
            return self.__email.value

        @property
        def name(self):
            """
            :type: :class:`string`
            """
            return self.__name.value

    def _initAttributes(self, author=_rcv.Absent, comment_count=_rcv.Absent, committer=_rcv.Absent, html_url=_rcv.Absent, message=_rcv.Absent, parents=_rcv.Absent, sha=_rcv.Absent, tree=_rcv.Absent, type=_rcv.Absent, **kwds):
        import PyGithub.Blocking.GitTree
        super(GitCommit, self)._initAttributes(**kwds)
        self.__author = _rcv.Attribute("GitCommit.author", _rcv.StructureConverter(self.Session, GitCommit.Author), author)
        self.__comment_count = _rcv.Attribute("GitCommit.comment_count", _rcv.IntConverter, comment_count)
        self.__committer = _rcv.Attribute("GitCommit.committer", _rcv.StructureConverter(self.Session, GitCommit.Author), committer)
        self.__html_url = _rcv.Attribute("GitCommit.html_url", _rcv.StringConverter, html_url)
        self.__message = _rcv.Attribute("GitCommit.message", _rcv.StringConverter, message)
        self.__parents = _rcv.Attribute("GitCommit.parents", _rcv.ListConverter(_rcv.ClassConverter(self.Session, GitCommit)), parents)
        self.__sha = _rcv.Attribute("GitCommit.sha", _rcv.StringConverter, sha)
        self.__tree = _rcv.Attribute("GitCommit.tree", _rcv.ClassConverter(self.Session, PyGithub.Blocking.GitTree.GitTree), tree)
        self.__type = _rcv.Attribute("GitCommit.type", _rcv.StringConverter, type)

    def _updateAttributes(self, eTag, author=_rcv.Absent, comment_count=_rcv.Absent, committer=_rcv.Absent, html_url=_rcv.Absent, message=_rcv.Absent, parents=_rcv.Absent, sha=_rcv.Absent, tree=_rcv.Absent, type=_rcv.Absent, **kwds):
        super(GitCommit, self)._updateAttributes(eTag, **kwds)
        self.__author.update(author)
        self.__comment_count.update(comment_count)
        self.__committer.update(committer)
        self.__html_url.update(html_url)
        self.__message.update(message)
        self.__parents.update(parents)
        self.__sha.update(sha)
        self.__tree.update(tree)
        self.__type.update(type)

    @property
    def author(self):
        """
        :type: :class:`.GitCommit.Author`
        """
        self._completeLazily(self.__author.needsLazyCompletion)
        return self.__author.value

    @property
    def comment_count(self):
        """
        :type: :class:`int`
        """
        self._completeLazily(self.__comment_count.needsLazyCompletion)
        return self.__comment_count.value

    @property
    def committer(self):
        """
        :type: :class:`.GitCommit.Author`
        """
        self._completeLazily(self.__committer.needsLazyCompletion)
        return self.__committer.value

    @property
    def html_url(self):
        """
        :type: :class:`string`
        """
        self._completeLazily(self.__html_url.needsLazyCompletion)
        return self.__html_url.value

    @property
    def message(self):
        """
        :type: :class:`string`
        """
        self._completeLazily(self.__message.needsLazyCompletion)
        return self.__message.value

    @property
    def parents(self):
        """
        :type: :class:`list` of :class:`~.GitCommit.GitCommit`
        """
        self._completeLazily(self.__parents.needsLazyCompletion)
        return self.__parents.value

    @property
    def sha(self):
        """
        :type: :class:`string`
        """
        self._completeLazily(self.__sha.needsLazyCompletion)
        return self.__sha.value

    @property
    def tree(self):
        """
        :type: :class:`~.GitTree.GitTree`
        """
        self._completeLazily(self.__tree.needsLazyCompletion)
        return self.__tree.value

    @property
    def type(self):
        """
        :type: :class:`string`
        """
        self._completeLazily(self.__type.needsLazyCompletion)
        return self.__type.value

    @property
    def url(self):
        """
        :type: :class:`string`
        """
        return self._url

    def update(self):
        """
        Makes a `conditional request <http://developer.github.com/v3/#conditional-requests>`_ and updates the object.
        Returns True if the object was updated.

        :rtype: :class:`bool`
        """
        return self._update()

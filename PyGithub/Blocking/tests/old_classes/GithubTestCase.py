# -*- coding: utf-8 -*-

# Copyright 2013-2014 Vincent Jacques <vincent@vincent-jacques.net>

import textwrap
import datetime

import PyGithub.Blocking
import PyGithub.Blocking.tests.Framework as Framework


class GithubTestCase(Framework.SimpleLoginTestCase):
    def testGetAuthenticatedUser(self):
        u = self.g.get_authenticated_user()
        self.assertEqual(u.login, "jacquev6")

    def testGetUser(self):
        u = self.g.get_user("nvie")
        self.assertEqual(u.name, "Vincent Driessen")

    def testGetUsers(self):
        users = self.g.get_users()
        self.assertEqual(users[0].login, "mojombo")
        self.assertEqual(users[1].login, "defunkt")

    def testGetUsersSinceId(self):
        users = self.g.get_users(since=327146)
        self.assertEqual(users[0].login, "FRINOS")
        self.assertEqual(users[1].login, "vangu90")

    def testGetUsersSinceUser(self):
        jacquev6 = self.g.get_user("jacquev6")
        users = self.g.get_users(since=jacquev6)
        self.assertEqual(users[0].login, "FRINOS")
        self.assertEqual(users[1].login, "vangu90")

    def testGetOrg(self):
        u = self.g.get_org("github")
        self.assertEqual(u.name, "GitHub")

    def testGetRepo(self):
        r = self.g.get_repo("nvie/gitflow")
        self.assertEqual(r.full_name, "nvie/gitflow")

    def testGetRepos(self):
        repos = self.g.get_repos()
        self.assertEqual(repos[0].full_name, "mojombo/grit")
        self.assertEqual(repos[1].full_name, "wycats/merb-core")

    def testGetReposSinceId(self):
        repos = self.g.get_repos(since=3544490)
        self.assertEqual(repos[0].full_name, "dereuromark/setup")
        self.assertEqual(repos[1].full_name, "hwatcha/ror")

    def testGetReposSinceRepo(self):
        pygithub = self.g.get_repo("jacquev6/PyGithub")
        repos = self.g.get_repos(since=pygithub)
        self.assertEqual(repos[0].full_name, "dereuromark/setup")
        self.assertEqual(repos[1].full_name, "hwatcha/ror")

    def testPaginationOfGetReposSince(self):
        repos = self.g.get_repos(since=3544490)
        self.assertEqual(repos[149].full_name, "swoosh/Hello-World")

    def testGetGitIgnoreTemplate(self):
        template = self.g.get_gitignore_template("C")
        self.assertEqual(template.name, "C")
        expectedSource = textwrap.dedent("""\
        # Object files
        *.o
        *.ko

        # Libraries
        *.lib
        *.a

        # Shared objects (inc. Windows DLLs)
        *.dll
        *.so
        *.so.*
        *.dylib

        # Executables
        *.exe
        *.out
        *.app
        """)
        self.assertEqual(template.source, expectedSource)

    def testGetGitIgnoreTemplates(self):
        # @todoAlpha Consider returning a list of GitIgnoreTemplate, even if the API is inconsistent. In that case, make GitIgnoreTemplate updatable
        templates = self.g.get_gitignore_templates()
        self.assertEqual(len(templates), 81)
        self.assertEqual(
            templates[:5],
            [
                "Actionscript",
                "Android",
                "AppceleratorTitanium",
                "Autotools",
                "Bancha",
            ]
        )
        self.assertEqual(
            templates[-5:],
            [
                "Yii",
                "ZendFramework",
                "gcov",
                "nanoc",
                "opencart",
            ]
        )

    def testGetPublicGists(self):
        gists = self.g.get_public_gists()
        self.assertEqual(gists[0].created_at, datetime.datetime(2014, 7, 12, 2, 35, 47))
        self.assertEqual(gists[0].updated_at, datetime.datetime(2014, 7, 12, 2, 35, 48))
        self.assertEqual(gists[1].created_at, datetime.datetime(2014, 7, 12, 2, 35, 18))
        self.assertEqual(gists[1].updated_at, datetime.datetime(2014, 7, 12, 2, 35, 19))
        self.assertEqual(gists[5].created_at, datetime.datetime(2014, 7, 12, 2, 32, 23))
        self.assertEqual(gists[5].updated_at, datetime.datetime(2014, 7, 12, 2, 32, 24))

    def testGetPublicGists_allParameters(self):
        # I don't really understand the effect of the 'since' parameter
        gists = self.g.get_public_gists(since=datetime.datetime(2014, 7, 12, 2, 30, 0), per_page=10)
        self.assertEqual(len(gists[:]), 33)
        self.assertEqual(gists[0].created_at, datetime.datetime(2014, 7, 12, 2, 45, 23))
        self.assertEqual(gists[0].updated_at, datetime.datetime(2014, 7, 12, 2, 45, 24))
        self.assertEqual(gists[32].created_at, datetime.datetime(2010, 4, 24, 23, 17, 32))
        self.assertEqual(gists[32].updated_at, datetime.datetime(2014, 7, 12, 2, 42, 25))

    def testCreateAnonymousGist(self):
        g = self.g.create_anonymous_gist(files={"foo.txt": {"content": "barbaz"}})
        self.assertIsNone(g.owner)
        self.assertIsNone(g.user)
        self.assertEqual(g.public, False)
        with self.assertRaises(PyGithub.Blocking.ObjectNotFoundException):
            g.delete()

    def testCreateAnonymousGist_allParameters(self):
        g = self.g.create_anonymous_gist(files={"foo.txt": {"content": "barbaz"}}, description="Created by PyGithub", public=True)
        self.assertIsNone(g.owner)
        self.assertIsNone(g.user)
        self.assertEqual(g.description, "Created by PyGithub")
        self.assertEqual(g.public, True)
        with self.assertRaises(PyGithub.Blocking.ObjectNotFoundException):
            g.delete()

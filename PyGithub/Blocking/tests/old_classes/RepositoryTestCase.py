# -*- coding: utf-8 -*-

# Copyright 2013-2014 Vincent Jacques <vincent@vincent-jacques.net>

import datetime

import PyGithub.Blocking
import PyGithub.Blocking.Dir
import PyGithub.Blocking.File
import PyGithub.Blocking.User

import PyGithub.Blocking.tests.Framework as Framework
from PyGithub.Blocking.tests.Framework import *


class RepositoryTestCase(Framework.SimpleLoginTestCase):
    def testGetStargazers(self):
        users = self.g.get_repo("jacquev6/PyGithub").get_stargazers(per_page=3)
        self.assertEqual(users[0].login, "ybakos")
        self.assertEqual(users[1].login, "huxley")

    def testGetSubscribers(self):
        users = self.g.get_repo("jacquev6/PyGithub").get_subscribers()
        self.assertEqual(users[0].login, "jacquev6")
        self.assertEqual(users[1].login, "equus12")

    def testGetSubscribers_allParameters(self):
        users = self.g.get_repo("jacquev6/PyGithub").get_subscribers(per_page=3)
        self.assertEqual(users[0].login, "jacquev6")
        self.assertEqual(users[1].login, "equus12")

    def testGetForks(self):
        repos = self.g.get_repo("jacquev6/PyGithub").get_forks()
        self.assertEqual(repos[0].owner.login, "Web5design")
        self.assertEqual(repos[1].owner.login, "pelson")

    def testGetForks_allParameters(self):
        repos = self.g.get_repo("jacquev6/PyGithub").get_forks(sort="stargazers", per_page=3)
        self.assertEqual(repos[0].owner.login, "roverdotcom")
        self.assertEqual(repos[0].stargazers_count, 1)
        self.assertEqual(repos[1].owner.login, "pmuilu")
        self.assertEqual(repos[1].stargazers_count, 1)

    def testGetTeamsOfPersonalRepo(self):
        teams = self.g.get_repo("jacquev6/PyGithub").get_teams()
        self.assertEqual(len(list(teams)), 0)

    def testGetTeamsOfOrgRepo(self):
        teams = self.g.get_repo("BeaverSoftware/FatherBeaver").get_teams()
        self.assertEqual(teams[0].name, "Members")

    def testGetTeams_allParameters(self):
        teams = self.g.get_repo("BeaverSoftware/FatherBeaver").get_teams(per_page=1)
        self.assertEqual(teams[0].name, "Members")

    def testGetKeys(self):
        keys = self.g.get_repo("jacquev6/CodingDojos").get_keys()
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0].id, 6941367)

    def testGetKey(self):
        key = self.g.get_repo("jacquev6/CodingDojos").get_key(6941367)
        self.assertEqual(key.title, "dojo@dojo")

    def testCreateKey(self):
        key = self.g.get_repo("jacquev6/CodingDojos").create_key("vincent@test", "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCkQih2DtSwBzLUtSNYEKULlI5M1qa6vnq42xt9qZpkLav3G9eD/GqJRST+zZMsyfpP62PtiYKXJdLJX2MQIzUgI2PzNy+iMy+ldiTEABYEOCa+BH9+x2R5xXGlmmCPblpamx3kstGtCTa3LSkyIvxbt5vjbXCyThhJaSKyh+42Uedcz7l0y/TODhnkpid/5eiBz6k0VEbFfhM6h71eBdCFpeMJIhGaPTjbKsEjXIK0SRe0v0UQnpXJQkhAINbm+q/2yjt7zwBF74u6tQjRqJK7vQO2k47ZmFMAGeIxS6GheI+JPmwtHkxvfaJjy2lIGX+rt3lkW8xEUxiMTlxeh+0R")
        self.assertEqual(key.id, 7229238)

    def testGetReadme(self):
        readme = self.g.get_repo("jacquev6/PyGithubIntegrationTests").get_readme()
        self.assertEqual(readme.url, "https://api.github.com/repos/jacquev6/PyGithubIntegrationTests/contents/README.md?ref=master")

    def testGetReadme_allParameters(self):
        # @todoAlpha ref can also be a GitObject
        readme = self.g.get_repo("jacquev6/PyGithubIntegrationTests").get_readme(ref="develop")
        self.assertEqual(readme.url, "https://api.github.com/repos/jacquev6/PyGithubIntegrationTests/contents/README.md?ref=develop")

    def testGetFileContents(self):
        f = self.g.get_repo("jacquev6/PyGithubIntegrationTests").get_contents("README.md")
        self.assertIsInstance(f, PyGithub.Blocking.File.File)
        self.assertEqual(f.type, "file")
        self.assertEqual(f.url, "https://api.github.com/repos/jacquev6/PyGithubIntegrationTests/contents/README.md?ref=master")

    def testGetSymlinkContents(self):
        f = self.g.get_repo("jacquev6/PyGithubIntegrationTests").get_contents("SymLink.rst")
        self.assertIsInstance(f, PyGithub.Blocking.SymLink.SymLink)
        self.assertEqual(f.type, "symlink")
        self.assertEqual(f.url, "https://api.github.com/repos/jacquev6/PyGithubIntegrationTests/contents/SymLink.rst?ref=master")

    def testGetSubmoduleContents(self):
        f = self.g.get_repo("jacquev6/PyGithubIntegrationTests").get_contents("PyGithub")
        self.assertIsInstance(f, PyGithub.Blocking.Submodule.Submodule)
        self.assertEqual(f.type, "submodule")
        self.assertEqual(f.url, "https://api.github.com/repos/jacquev6/PyGithubIntegrationTests/contents/PyGithub?ref=master")

    def testGetFileContentsWithinDirectory(self):
        f = self.g.get_repo("jacquev6/PyGithubIntegrationTests").get_contents("a/foo.md")
        self.assertIsInstance(f, PyGithub.Blocking.File.File)
        self.assertEqual(f.type, "file")
        self.assertEqual(f.url, "https://api.github.com/repos/jacquev6/PyGithubIntegrationTests/contents/a/foo.md?ref=master")

    def testGetFileContents_allParameters(self):
        f = self.g.get_repo("jacquev6/PyGithubIntegrationTests").get_contents("toto.md", ref="develop")
        self.assertIsInstance(f, PyGithub.Blocking.File.File)
        self.assertEqual(f.type, "file")
        self.assertEqual(f.url, "https://api.github.com/repos/jacquev6/PyGithubIntegrationTests/contents/toto.md?ref=develop")

    def testGetRootDirContents(self):
        contents = self.g.get_repo("jacquev6/PyGithubIntegrationTests").get_contents("")
        self.assertIsInstance(contents, list)
        self.assertEqual(len(contents), 5)
        self.assertIsInstance(contents[0], PyGithub.Blocking.File.File)
        self.assertIsInstance(contents[1], PyGithub.Blocking.Submodule.Submodule)
        self.assertIsInstance(contents[2], PyGithub.Blocking.File.File)
        self.assertIsInstance(contents[3], PyGithub.Blocking.SymLink.SymLink)
        self.assertIsInstance(contents[4], PyGithub.Blocking.Repository.Repository.Dir)
        self.assertEqual(contents[0].type, "file")
        self.assertEqual(contents[1].type, "file")  # https://github.com/github/developer.github.com/commit/1b329b04cece9f3087faa7b1e0382317a9b93490
        self.assertEqual(contents[2].type, "file")
        self.assertEqual(contents[3].type, "symlink")
        self.assertEqual(contents[4].type, "dir")

    def testCreateFile(self):
        cc = self.g.get_repo("jacquev6/PyGithubIntegrationTests").create_file("hello.md", "Add hello.md", "SGVsbG8sIFdvcmxkIQ==")
        self.assertEqual(cc.content.size, 13)
        self.assertEqual(cc.content.url, "https://api.github.com/repos/jacquev6/PyGithubIntegrationTests/contents/hello.md?ref=master")
        self.assertEqual(cc.commit.url, "https://api.github.com/repos/jacquev6/PyGithubIntegrationTests/git/commits/4289f250d2144c637b255e5765ef0fac00f4d8d4")

    def testCreateFile_allParameters(self):
        cc = self.g.get_repo("jacquev6/PyGithubIntegrationTests").create_file(
            "hello.md",
            "Add hello.md",
            "SGVsbG8sIFdvcmxkIQ==",
            branch="develop",
            committer={"name": "John Doe", "email": "john@doe.com"},
            author={"name": "Jane Doe", "email": "jane@doe.com"},  # @todoAlpha Use a GitCommit.Author? Does the api accept an undocumented date?
        )
        self.assertEqual(cc.content.size, 13)
        self.assertEqual(cc.content.url, "https://api.github.com/repos/jacquev6/PyGithubIntegrationTests/contents/hello.md?ref=develop")
        self.assertEqual(cc.commit.author.name, "Jane Doe")
        self.assertEqual(cc.commit.committer.email, "john@doe.com")

# -*- coding: utf-8 -*-

# Copyright 2013-2014 Vincent Jacques <vincent@vincent-jacques.net>

from PyGithub.Blocking.tests.Framework import *


class SubscriptionAttributes(TestCase):
    def test(self):
        s = self.user2.get_authenticated_user().get_subscription(("ghe-user-1", "repo-user-1-1"))
        self.assertEqual(s.created_at, datetime.datetime(2014, 7, 23, 1, 43, 22))
        self.assertEqual(s.ignored, False)
        self.assertIsNone(s.reason)
        self.assertEqual(s.repository_url, "http://github.home.jacquev6.net/api/v3/repos/ghe-user-1/repo-user-1-1")
        self.assertEqual(s.subscribed, True)


class SubscriptionEdit(TestCase):
    def test(self):
        s = self.user2.get_authenticated_user().get_subscription(("ghe-user-1", "repo-user-1-1"))
        s.edit(subscribed=False, ignored=True)
        self.assertEqual(s.subscribed, False)
        self.assertEqual(s.ignored, True)
        s.edit(subscribed=True, ignored=False)
        self.assertEqual(s.subscribed, True)
        self.assertEqual(s.ignored, False)


class SubscriptionDelete(TestCase):
    def test(self):
        s = self.user2.get_authenticated_user().create_subscription(("ghe-org-1", "repo-org-1-1"), subscribed=True, ignored=False)
        s.delete()

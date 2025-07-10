from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ....core import model_factories as core_factories
from ....core.tests import utils as test_utils
from ... import model_factories as posts_factories
from ... import models as posts_models


class TagListTest(APITestCase):
    def setUp(self):
        self.user1 = core_factories.UserFactory()
        self.author_group = Group.objects.create(name="author")
        self.user1.groups.add(self.author_group)
        self.tag = posts_factories.TagFactory()
        self.url = reverse("tag-list")
        return super().setUp()

    def test_get_guest(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        tag_id = test_utils.last_url_pk(res.data[0]["url"])
        self.assertEqual(self.tag.id, tag_id)

    def test_post_put_patch_delete_guest(self):
        methods = ["post", "put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.url)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_login(self):
        test_utils.jwt_login(self.client, self.user1.username)

        title = "wahoo"
        self.assertFalse(posts_models.Tag.objects.filter(title=title).exists())

        res = self.client.post(self.url, {"title": title})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(posts_models.Tag.objects.filter(title=title).exists())

    def test_put_patch_delete_login(self):
        test_utils.jwt_login(self.client, self.user1.username)

        methods = ["put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.url)

            self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_login_not_author(self):
        self.user1.groups.remove(self.author_group)
        test_utils.jwt_login(self.client, self.user1.username)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.post(self.url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

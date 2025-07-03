import datetime
from unittest import mock

from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ....core import model_factories as core_factories
from ....core.tests import utils as test_utils
from ... import model_factories as posts_factories
from ... import models as posts_models


class PostListTest(APITestCase):
    def setUp(self):
        def clean_excluding_thumbnail(self, exclude=None):
            exclude = list(exclude or []) + ["thumbnail"]
            super(posts_models.Post, self).clean_fields(exclude=exclude)

        patcher = mock.patch("apps.posts.models.Post.clean_fields", autospec=True)
        self.mock_clean_fields = patcher.start()
        self.mock_clean_fields.side_effect = clean_excluding_thumbnail
        self.addCleanup(patcher.stop)

        self.user1 = core_factories.UserFactory()
        self.author_group = Group.objects.create(name="author")
        self.user1.groups.add(self.author_group)
        self.public_post = posts_factories.PostFactory(
            owner=self.user1,
            thumbnail="https://fake-url.com/media/thumbnail.webp",
            publish_date=datetime.date.today(),
            tags=[posts_factories.TagFactory()],
        )

        self.user2 = core_factories.UserFactory()
        self.user2.groups.add(self.author_group)
        self.private_post = posts_factories.PostFactory(owner=self.user2)

        self.url = reverse("post-list")
        return super().setUp()

    def test_get_guest(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Private post hidden, public visible
        self.assertEqual(len(res.data), 1)
        post_id = test_utils.last_url_pk(res.data[0]["url"])
        self.assertEqual(self.public_post.id, post_id)

    def test_post_put_patch_delete_guest(self):
        methods = ["post", "put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.url)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_login(self):
        # List two posts, 1 public and 1 private
        # First, user2 that owns private post
        test_utils.jwt_login(self.client, self.user2.username)

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        # Second, user1 that owns public post
        test_utils.jwt_login(self.client, self.user1.username)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        post_id = test_utils.last_url_pk(res.data[0]["url"])
        self.assertEqual(self.public_post.id, post_id)

    def test_post_login(self):
        test_utils.jwt_login(self.client, self.user1.username)

        title = "This title is at least min length"
        res = self.client.post(self.url, {"title": title})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(posts_models.Post.objects.filter(title=title).exists())

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

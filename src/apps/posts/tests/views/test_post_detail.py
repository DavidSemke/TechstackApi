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


class PostDetailTest(APITestCase):
    def get_url(self, post_id):
        return reverse("post-detail", kwargs={"pk": post_id})

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

        self.tags = [posts_factories.TagFactory()]
        self.public_post = posts_factories.PostFactory(
            owner=self.user1,
            thumbnail="https://fake-url.com/media/thumbnail.webp",
            publish_date=datetime.date.today(),
            tags=self.tags,
        )
        self.public_url = self.get_url(self.public_post.id)
        return super().setUp()

    def test_get_guest_public_post(self):
        res = self.client.get(self.public_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post_id = test_utils.last_url_pk(res.data["url"])
        self.assertEqual(self.public_post.id, post_id)

    def test_get_guest_private_post(self):
        private_post = posts_factories.PostFactory(owner=self.user1)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.get(self.get_url(private_post.id))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_put_patch_delete_guest(self):
        methods = ["post", "put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.public_url)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_login_private_post(self):
        user2 = core_factories.UserFactory()
        user2.groups.add(self.author_group)
        test_utils.jwt_login(self.client, user2.username)
        private_post = posts_factories.PostFactory(owner=self.user1)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.get(self.get_url(private_post.id))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_login(self):
        test_utils.jwt_login(self.client, self.user1.username)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.post(self.public_url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_patch_delete_login_public_post(self):
        user2 = core_factories.UserFactory()
        user2.groups.add(self.author_group)
        test_utils.jwt_login(self.client, user2.username)

        methods = ["put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.public_url)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_login_private_post_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)
        private_post = posts_factories.PostFactory(owner=self.user1)

        res = self.client.get(self.get_url(private_post.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_put_login_public_post_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)

        new_title = "This title is at least min length"
        self.assertNotEqual(self.public_post.title, new_title)

        res = self.client.put(
            self.public_url,
            {"title": new_title, "tags": self.tags},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.public_post.refresh_from_db()
        self.assertEqual(self.public_post.title, new_title)

    def test_patch_login_public_post_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)

        new_title = "This title is at least min length"
        self.assertNotEqual(self.public_post.title, new_title)

        res = self.client.patch(
            self.public_url,
            {"title": new_title},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.public_post.refresh_from_db()
        self.assertEqual(self.public_post.title, new_title)

    def test_delete_login_public_post_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)

        res = self.client.delete(self.public_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(posts_models.Post.DoesNotExist):
            self.public_post.refresh_from_db()

    def test_put_patch_delete_login_public_post_owner_not_author(self):
        self.user1.groups.remove(self.author_group)
        test_utils.jwt_login(self.client, self.user1.username)

        methods = ["put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.public_url)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

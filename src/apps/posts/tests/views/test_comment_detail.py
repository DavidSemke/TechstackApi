from unittest import mock

from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ....core import model_factories as core_factories
from ....core.tests import utils as test_utils
from ... import model_factories as posts_factories
from ... import models as posts_models


class CommentDetailTest(APITestCase):
    def get_url(self, comment_id):
        return reverse("comment-detail", kwargs={"pk": comment_id})

    def setUp(self):
        def clean_excluding_thumbnail(self, exclude=None):
            exclude = list(exclude or []) + ["thumbnail"]
            super(posts_models.Post, self).clean_fields(exclude=exclude)

        patcher = mock.patch("apps.posts.models.Post.clean_fields", autospec=True)
        self.mock_clean_fields = patcher.start()
        self.mock_clean_fields.side_effect = clean_excluding_thumbnail
        self.addCleanup(patcher.stop)

        self.user1 = core_factories.UserFactory()
        self.commenter_group = Group.objects.create(name="commenter")
        self.user1.groups.add(self.commenter_group)

        self.post = posts_factories.PostFactory(
            owner=self.user1,
            thumbnail="https://fake-url.com/media/thumbnail.webp",
            tags=[posts_factories.TagFactory()],
        )
        self.comment = posts_factories.CommentFactory(owner=self.user1, post=self.post)
        self.comment_url = self.get_url(self.comment.id)
        return super().setUp()

    def test_get_guest(self):
        res = self.client.get(self.comment_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        comment_id = test_utils.last_url_pk(res.data["url"])
        self.assertEqual(self.comment.id, comment_id)

    def test_get_guest_private_post(self):
        self.post.publish_date = None
        self.post.save()

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.get(self.comment_url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_put_patch_delete_guest(self):
        methods = ["post", "put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.comment_url)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_login_private_post(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)
        self.post.publish_date = None
        self.post.save()

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.get(self.comment_url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_login(self):
        test_utils.jwt_login(self.client, self.user1.username)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.post(self.comment_url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_patch_delete_login_public_post(self):
        user2 = core_factories.UserFactory()
        user2.groups.add(self.commenter_group)
        test_utils.jwt_login(self.client, user2.username)

        methods = ["put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.comment_url)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_login_private_post_comment_owner(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)
        private_post_comment = posts_factories.CommentFactory(
            owner=user2, post=self.post
        )
        self.post.publish_date = None
        self.post.save()

        res = self.client.get(self.get_url(private_post_comment.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_login_private_post_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)
        user2 = core_factories.UserFactory()
        private_post_comment = posts_factories.CommentFactory(
            owner=user2, post=self.post
        )
        self.post.publish_date = None
        self.post.save()

        res = self.client.get(self.get_url(private_post_comment.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_put_login_public_post_comment_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)

        new_content = "hello"
        self.assertNotEqual(self.comment.content, new_content)

        res = self.client.put(self.comment_url, {"content": new_content})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, new_content)

    def test_patch_login_public_post_comment_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)

        new_content = "hello"
        self.assertNotEqual(self.comment.content, new_content)

        res = self.client.patch(self.comment_url, {"content": new_content})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, new_content)

    def test_delete_login_public_post_comment_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)

        res = self.client.delete(self.comment_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(posts_models.Comment.DoesNotExist):
            self.comment.refresh_from_db()

    def test_put_patch_delete_login_private_post_comment_owner(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)
        private_post_comment = posts_factories.ReactionFactory(
            owner=user2, post=self.post
        )
        self.post.publish_date = None
        self.post.save()

        methods = ["put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.get_url(private_post_comment.id))

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_patch_delete_login_owner_not_commenter(self):
        self.user1.groups.remove(self.commenter_group)
        test_utils.jwt_login(self.client, self.user1.username)

        methods = ["put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.comment_url)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

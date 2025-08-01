from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ....core import model_factories as core_factories
from ....core.tests import utils as test_utils
from ... import model_factories as posts_factories
from ... import models as posts_models


class ReactionDetailTest(APITestCase):
    def get_url(self, reaction_id):
        return reverse("reaction-detail", kwargs={"pk": reaction_id})

    def setUp(self):
        def clean_excluding_thumbnail(self, exclude=None):
            exclude = list(exclude or []) + ["thumbnail"]
            super(posts_models.Post, self).clean_fields(exclude=exclude)

        patcher = mock.patch("apps.posts.models.Post.clean_fields", autospec=True)
        self.mock_clean_fields = patcher.start()
        self.mock_clean_fields.side_effect = clean_excluding_thumbnail
        self.addCleanup(patcher.stop)

        self.user1 = core_factories.UserFactory()
        self.post = posts_factories.PostFactory(
            owner=self.user1,
            thumbnail="https://fake-url.com/media/thumbnail.webp",
            tags=[posts_factories.TagFactory()],
        )
        self.post_reaction = posts_factories.ReactionFactory(
            owner=self.user1, post=self.post
        )
        self.post_reaction_url = self.get_url(self.post_reaction.id)
        return super().setUp()

    def test_get_guest(self):
        res = self.client.get(self.post_reaction_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        reaction_id = test_utils.last_url_pk(res.data["url"])
        self.assertEqual(self.post_reaction.id, reaction_id)

    def test_get_guest_private_post(self):
        self.post.publish_date = None
        self.post.save()

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.get(self.post_reaction_url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_put_patch_delete_guest(self):
        methods = ["post", "put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.post_reaction_url)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_login_private_post(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)
        self.post.publish_date = None
        self.post.save()

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.get(self.post_reaction_url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_login(self):
        test_utils.jwt_login(self.client, self.user1.username)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.post(self.post_reaction_url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_patch_delete_login_public_post(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)

        methods = ["put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.post_reaction_url)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_login_private_post_post_reaction_owner(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)
        private_post_reaction = posts_factories.ReactionFactory(
            owner=user2, post=self.post
        )
        self.post.publish_date = None
        self.post.save()

        res = self.client.get(self.get_url(private_post_reaction.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_login_private_post_comment_reaction_owner(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)
        private_post_comment = posts_factories.CommentFactory(
            owner=self.user1, post=self.post
        )
        private_post_reaction = posts_factories.ReactionFactory(
            owner=user2, comment=private_post_comment
        )
        self.post.publish_date = None
        self.post.save()

        res = self.client.get(self.get_url(private_post_reaction.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_login_private_post_owner_post_reaction(self):
        test_utils.jwt_login(self.client, self.user1.username)
        user2 = core_factories.UserFactory()
        private_post_reaction = posts_factories.ReactionFactory(
            owner=user2, post=self.post
        )
        self.post.publish_date = None
        self.post.save()

        res = self.client.get(self.get_url(private_post_reaction.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_login_private_post_owner_comment_reaction(self):
        test_utils.jwt_login(self.client, self.user1.username)
        user2 = core_factories.UserFactory()
        private_post_comment = posts_factories.CommentFactory(
            owner=user2, post=self.post
        )
        private_post_reaction = posts_factories.ReactionFactory(
            owner=user2, comment=private_post_comment
        )
        self.post.publish_date = None
        self.post.save()

        res = self.client.get(self.get_url(private_post_reaction.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_put_login_public_post_post_reaction_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)

        if self.post_reaction.type == "L":
            new_type = "D"
        else:
            new_type = "L"

        res = self.client.put(
            self.post_reaction_url, {"type": new_type, "post": self.post.id}
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.post_reaction.refresh_from_db()
        self.assertEqual(self.post_reaction.type, new_type)

    def test_put_login_public_post_comment_reaction_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)
        comment = posts_factories.CommentFactory(owner=self.user1, post=self.post)
        comment_reaction = posts_factories.ReactionFactory(
            owner=self.user1, comment=comment
        )

        if comment_reaction.type == "L":
            new_type = "D"
        else:
            new_type = "L"

        res = self.client.put(
            self.get_url(comment_reaction.id), {"type": new_type, "comment": comment.id}
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        comment_reaction.refresh_from_db()
        self.assertEqual(comment_reaction.type, new_type)

    def test_patch_login_public_post_post_reaction_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)

        if self.post_reaction.type == "L":
            new_type = "D"
        else:
            new_type = "L"

        res = self.client.patch(self.post_reaction_url, {"type": new_type})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.post_reaction.refresh_from_db()
        self.assertEqual(self.post_reaction.type, new_type)

    def test_patch_login_public_post_comment_reaction_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)
        comment = posts_factories.CommentFactory(owner=self.user1, post=self.post)
        comment_reaction = posts_factories.ReactionFactory(
            owner=self.user1, comment=comment
        )

        if comment_reaction.type == "L":
            new_type = "D"
        else:
            new_type = "L"

        res = self.client.patch(self.get_url(comment_reaction.id), {"type": new_type})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        comment_reaction.refresh_from_db()
        self.assertEqual(comment_reaction.type, new_type)

    def test_delete_login_public_post_post_reaction_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)

        res = self.client.delete(self.post_reaction_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(posts_models.Reaction.DoesNotExist):
            self.post_reaction.refresh_from_db()

    def test_delete_login_public_post_comment_reaction_owner(self):
        test_utils.jwt_login(self.client, self.user1.username)
        comment = posts_factories.CommentFactory(owner=self.user1, post=self.post)
        comment_reaction = posts_factories.ReactionFactory(
            owner=self.user1, comment=comment
        )

        res = self.client.delete(self.get_url(comment_reaction.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(posts_models.Reaction.DoesNotExist):
            comment_reaction.refresh_from_db()

    def test_delete_login_private_post_post_reaction_owner(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)
        private_post_reaction = posts_factories.ReactionFactory(
            owner=user2, post=self.post
        )
        self.post.publish_date = None
        self.post.save()

        res = self.client.delete(self.get_url(private_post_reaction.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

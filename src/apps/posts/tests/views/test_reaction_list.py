import datetime
from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ....core import model_factories as core_factories
from ....core.tests import utils as test_utils
from ... import model_factories as posts_factories
from ... import models as posts_models


class ReactionListTest(APITestCase):
    def setUp(self):
        def clean_excluding_thumbnail(self, exclude=None):
            exclude = list(exclude or []) + ["thumbnail"]
            super(posts_models.Post, self).clean_fields(exclude=exclude)

        patcher = mock.patch("apps.posts.models.Post.clean_fields", autospec=True)
        self.mock_clean_fields = patcher.start()
        self.mock_clean_fields.side_effect = clean_excluding_thumbnail
        self.addCleanup(patcher.stop)

        self.user1 = core_factories.UserFactory()
        self.public_post = posts_factories.PostFactory(
            owner=self.user1,
            thumbnail="https://fake-url.com/media/thumbnail.webp",
            publish_date=datetime.date.today(),
            tags=[posts_factories.TagFactory()],
        )
        self.post_reaction = posts_factories.ReactionFactory(
            owner=self.user1, post=self.public_post
        )
        self.url = reverse("reaction-list")
        return super().setUp()

    def test_get_guest(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        reaction_id = test_utils.last_url_pk(res.data[0]["url"])
        self.assertEqual(self.post_reaction.id, reaction_id)

    def test_post_put_patch_delete_guest(self):
        methods = ["post", "put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.url)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_login_target_post(self):
        test_utils.jwt_login(self.client, self.user1.username)

        self.assertFalse(
            posts_models.Reaction.objects.filter(
                owner=self.user1, post=self.public_post
            ).exists()
        )
        res = self.client.post(self.url, {"post": self.public_post.id, "type": "L"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            posts_models.Reaction.objects.filter(
                owner=self.user1, post=self.public_post
            ).exists()
        )

    def test_post_login_target_comment(self):
        test_utils.jwt_login(self.client, self.user1.username)

        comment = posts_factories.CommentFactory(
            owner=self.user1, post=self.public_post
        )
        self.assertFalse(
            posts_models.Reaction.objects.filter(
                owner=self.user1, comment=comment
            ).exists()
        )
        res = self.client.post(self.url, {"comment": comment.id, "type": "L"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            posts_models.Reaction.objects.filter(
                owner=self.user1, comment=comment
            ).exists()
        )

    def test_put_patch_delete_login(self):
        test_utils.jwt_login(self.client, self.user1.username)

        methods = ["put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.url)

            self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

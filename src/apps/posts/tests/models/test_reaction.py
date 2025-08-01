from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase

from ....core import model_factories as core_factories
from ... import model_factories as posts_factories
from ... import models as posts_models


class ReactionModelTest(TestCase):
    def setUp(self):
        def clean_excluding_thumbnail(self, exclude=None):
            exclude = list(exclude or []) + ["thumbnail"]
            super(posts_models.Post, self).clean_fields(exclude=exclude)

        patcher = mock.patch("apps.posts.models.Post.clean_fields", autospec=True)
        self.mock_clean_fields = patcher.start()
        self.mock_clean_fields.side_effect = clean_excluding_thumbnail
        self.addCleanup(patcher.stop)

        self.user1 = core_factories.UserFactory()
        self.tag1 = posts_factories.TagFactory()
        self.post = posts_factories.PostFactory(
            owner=self.user1,
            thumbnail="https://fake-url.com/media/thumbnail.webp",
            tags=[self.tag1],
        )
        self.post_reaction = posts_factories.ReactionFactory(
            owner=self.user1, post=self.post
        )
        return super().setUp()

    def test_constraint_exactly_one_target(self):
        self.post_reaction.comment = posts_factories.CommentFactory(
            owner=self.user1, post=self.post
        )

        with self.assertRaises(ValidationError) as context:
            self.post_reaction.save()

        error_messages = context.exception.messages
        self.assertEqual(len(error_messages), 1)
        self.assertIn("exactly_one_reaction_target", error_messages[0])

    def test_constraint_unique_owner_post(self):
        with self.assertRaises(ValidationError) as context:
            posts_factories.ReactionFactory(owner=self.user1, post=self.post)

        error_messages = context.exception.messages
        self.assertEqual(len(error_messages), 1)
        self.assertIn("unique_owner_post", error_messages[0])

    def test_constraint_unique_owner_comment(self):
        comment = posts_factories.CommentFactory(owner=self.user1, post=self.post)
        posts_factories.ReactionFactory(owner=self.user1, comment=comment)

        with self.assertRaises(ValidationError) as context:
            posts_factories.ReactionFactory(
                owner=self.user1,
                comment=comment,
            )

        error_messages = context.exception.messages
        self.assertEqual(len(error_messages), 1)
        self.assertIn("unique_owner_comment", error_messages[0])

    def test_post_private(self):
        self.post.publish_date = None
        self.post.save()

        with self.assertRaises(ValidationError) as context:
            self.post_reaction.save()

        error_messages = context.exception.messages
        self.assertEqual(len(error_messages), 1)
        self.assertEqual(error_messages[0], "A reaction cannot target a private post.")

    def test_comment_private(self):
        private_comment = posts_factories.CommentFactory(
            owner=self.user1,
            post=self.post,
        )
        self.post.publish_date = None
        self.post.save()

        with self.assertRaises(ValidationError) as context:
            posts_factories.ReactionFactory(
                owner=self.user1,
                comment=private_comment,
            )

        error_messages = context.exception.messages
        self.assertEqual(len(error_messages), 1)
        self.assertEqual(
            error_messages[0], "A reaction cannot target a comment of a private post."
        )

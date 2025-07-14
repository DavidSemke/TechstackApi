from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase

from ....core import model_factories as core_factories
from ... import model_factories as posts_factories
from ... import models as posts_models


class CommentModelTest(TestCase):
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

        return super().setUp()

    def test_post_private(self):
        self.post.publish_date = None
        self.post.save()

        with self.assertRaises(ValidationError) as e:
            posts_factories.CommentFactory(
                owner=self.user1,
                post=self.post,
            )
            self.assertEqual(len(e.messages), 1)
            self.assertEqual(e.messages[0], "A comment cannot target a private post.")

    def test_reply_to_self(self):
        comment = posts_factories.CommentFactory(owner=self.user1, post=self.post)
        comment.reply_to = comment

        with self.assertRaises(ValidationError) as e:
            comment.save()
            self.assertEqual(len(e.messages), 1)
            self.assertEqual(e.messages[0], "A comment cannot be a reply to itself.")

    def test_reply_to_reply(self):
        comment = posts_factories.CommentFactory()
        reply = posts_factories.CommentFactory(reply_to=comment)

        with self.assertRaises(ValidationError) as e:
            posts_factories.CommentFactory(reply_to=reply)
            self.assertEqual(len(e.messages), 1)
            self.assertEqual(e.messages[0], "A comment cannot be a reply to a reply.")

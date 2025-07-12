from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase

from ....core import model_factories as core_factories
from ... import model_factories as posts_factories
from ... import models as posts_models


class PostModelTest(TestCase):
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

    def test_thumbnail_empty_on_publish(self):
        self.post.thumbnail = ""

        try:
            self.post.save()
            self.fail("Validation error not raised.")
        except ValidationError as e:
            self.assertEqual(len(e.messages), 1)
            self.assertEqual(e.messages[0], "A published post must have a thumbnail.")

    def test_content_empty_on_publish(self):
        self.post.content = ""

        try:
            self.post.save()
            self.fail("Validation error not raised.")
        except ValidationError as e:
            self.assertEqual(len(e.messages), 1)
            self.assertEqual(e.messages[0], "A published post must have content.")

    def test_tags_too_few_on_publish(self):
        try:
            self.post.tags.remove(self.tag1)
            self.fail("Validation error not raised.")
        except ValidationError as e:
            self.assertEqual(len(e.messages), 1)
            self.assertEqual(
                e.messages[0], "A published post must have at least 1 tag(s)."
            )

    def test_tags_too_many(self):
        new_tags = [posts_factories.TagFactory() for _ in range(5)]

        try:
            self.post.tags.add(*new_tags)
            self.fail("Validation error not raised.")
        except ValidationError as e:
            self.assertEqual(len(e.messages), 1)
            self.assertEqual(e.messages[0], "A post must have at most 5 tag(s).")

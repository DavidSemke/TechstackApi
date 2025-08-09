from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from ... import model_factories as posts_factories


class TagModelTest(TestCase):
    def test_constraint_lowercase_title(self):
        with self.assertRaises(IntegrityError) as context:
            posts_factories.TagFactory(title="UPPERCASE")

        self.assertIn("lowercase_title", str(context.exception))

    def test_title_regex(self):
        # Valid title
        tag1 = posts_factories.TagFactory(title="axe-40-salad")
        tag1.full_clean()

        # Invalid title
        with self.assertRaises(ValidationError) as context:
            tag2 = posts_factories.TagFactory(title="axe(40-salad)")
            tag2.full_clean()

        error_messages = context.exception.messages
        self.assertEqual(len(error_messages), 1)
        self.assertEqual(
            error_messages[0],
            "Tag title must only contain letters, numbers, and hyphens.",
        )

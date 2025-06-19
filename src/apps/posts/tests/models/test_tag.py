from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from ... import model_factories as posts_factories


class PostModelTest(TestCase):
    def test_constraint_lowercase_title(self):
        try:
            posts_factories.TagFactory(title="UPPERCASE")
            self.fail("Integrity error not raised.")
        except IntegrityError as e:
            self.assertIn("lowercase_title", str(e))

    def test_title_regex(self):
        # Valid title
        tag1 = posts_factories.TagFactory(title="axe-40-salad")
        tag1.full_clean()

        # Invalid title
        try:
            tag2 = posts_factories.TagFactory(title="axe(40-salad)")
            tag2.full_clean()
            self.fail("Validation error not raised.")
        except ValidationError as e:
            self.assertEqual(len(e.messages), 1)
            self.assertEqual(
                e.messages[0],
                "Tag title must only contain letters, numbers, and hyphens.",
            )

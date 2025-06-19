from django.db.utils import IntegrityError
from django.test import TestCase

from ....core import model_factories as core_factories
from ... import model_factories as posts_factories


class PostModelTest(TestCase):
    def setUp(self):
        self.user1 = core_factories.UserFactory()
        self.post = posts_factories.PostFactory(owner=self.user1)
        self.post_reaction = posts_factories.ReactionFactory(
            owner=self.user1, post=self.post
        )

    def test_constraint_exactly_one_target(self):
        self.post_reaction.comment = posts_factories.CommentFactory()

        try:
            self.post_reaction.save()
            self.fail("Integrity error not raised.")
        except IntegrityError as e:
            self.assertIn("exactly_one_reaction_target", str(e))

    def test_constraint_unique_owner_post(self):
        try:
            posts_factories.ReactionFactory(owner=self.user1, post=self.post)
            self.fail("Integrity error not raised.")
        except IntegrityError as e:
            self.assertIn("unique_owner_post", str(e))

    def test_constraint_unique_owner_comment(self):
        comment = posts_factories.CommentFactory()
        posts_factories.ReactionFactory(
            owner=self.user1,
            comment=comment,
        )

        try:
            posts_factories.ReactionFactory(
                owner=self.user1,
                comment=comment,
            )
            self.fail("Integrity error not raised.")
        except IntegrityError as e:
            self.assertIn("unique_owner_comment", str(e))

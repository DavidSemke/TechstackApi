import random

from decouple import config
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from ....core.model_factories import UserFactory
from ....posts.model_factories import (
    CommentFactory,
    PostFactory,
    ReactionFactory,
    TagFactory,
)
from ....posts.models import Comment, Post, Reaction, Tag


class Command(BaseCommand):
    help = "Insert placeholder data into the database."

    def handle(self, *args, **kwargs):
        self._clear_tables()

        self._insert_users()

        post_count = 12
        tag_count = post_count
        tags = self._insert_tags(tag_count)

        posts = self._insert_posts(tags, post_count)

        # Create 3 comments per post:
        # 1 - A non-reply, without a reply
        # 2 - A non-reply, with a reply
        # 3 - The reply
        nonreply_count = post_count * 2
        reply_count = post_count
        comments = self._insert_comments(nonreply_count, reply_count)

        # Create 1 reaction per post/comment
        reaction_count = post_count + nonreply_count + reply_count
        self._insert_reactions(posts, comments, reaction_count)

    def _clear_tables(self):
        User = get_user_model()

        for model in (User, Tag, Post, Comment, Reaction):
            model.objects.all().delete()

    # Handles 1-1 relationships (e.g. Profile)
    def _insert_users(self, count=3):
        self.stdout.write("Inserting users...")

        # Create admin user
        User = get_user_model()
        User.objects.create_superuser(
            username=config("ADMIN_USERNAME"),
            email=config("ADMIN_EMAIL"),
            password=config("ADMIN_PASSWORD"),
        )

        return [UserFactory() for _ in range(count)]

    def _insert_tags(self, count):
        if count < 0:
            raise ValueError("Count cannot be negative.")

        self.stdout.write("Inserting tags...")
        return [TagFactory() for _ in range(count)]

    def _insert_posts(self, tags, count):
        if count < 0:
            raise ValueError("Count cannot be negative.")

        self.stdout.write("Inserting posts...")
        return [PostFactory(tags=random.sample(tags, 5)) for _ in range(count)]

    def _insert_comments(self, nonreply_count, reply_count):
        if nonreply_count < 0 or reply_count < 0:
            raise ValueError("Counts cannot be negative.")

        if nonreply_count == 0 and reply_count > nonreply_count:
            raise ValueError("Cannot have replies without nonreplies.")

        self.stdout.write("Inserting comments...")
        nonreplies = [CommentFactory() for _ in range(nonreply_count)]
        replies = []

        for i in range(reply_count):
            nonreply = nonreplies[i % nonreply_count]
            replies.append(CommentFactory(reply_to=nonreply))

        return nonreplies + replies

    # Posts are given reactions before comments
    def _insert_reactions(self, posts, comments, count):
        if count < 0:
            raise ValueError("Count cannot be negative.")

        self.stdout.write("Inserting reactions...")
        post_count = len(posts)
        comment_count = len(comments)
        post_reactions = []
        comment_reactions = []
        reaction_index = 0

        while reaction_index < count:
            post_index = 0

            while post_index < post_count and reaction_index < count:
                post_reactions.append(ReactionFactory(post=posts[post_index]))
                post_index += 1
                reaction_index += 1

            comment_index = 0

            while comment_index < comment_count and reaction_index < count:
                comment_reactions.append(
                    ReactionFactory(comment=comments[comment_index])
                )
                comment_index += 1
                reaction_index += 1

        return post_reactions, comment_reactions

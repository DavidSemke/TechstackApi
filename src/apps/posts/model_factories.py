from django.contrib.auth import get_user_model
from factory import Faker, Iterator, LazyFunction, Sequence, Trait, post_generation
from factory.django import DjangoModelFactory

from ..core import utils as core_utils
from .models import Comment, Post, Reaction, Tag

User = get_user_model()


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    title = Sequence(lambda n: "tag-%04d" % n)


class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    title = Faker("text", max_nb_chars=100)
    thumbnail = LazyFunction(lambda: core_utils.rand_image_url())
    owner = Iterator(User.objects.filter(is_superuser=False))
    publish_date = Faker("date")
    content = Faker("text", max_nb_chars=3000)

    @post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        # Add the iterable of tags using bulk addition
        self.tags.add(*extracted)


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    owner = Iterator(User.objects.filter(is_superuser=False))
    post = Iterator(Post.objects.filter(publish_date__isnull=False))
    content = Faker("text", max_nb_chars=300)
    reply_to = None


class ReactionFactory(DjangoModelFactory):
    class Meta:
        model = Reaction

    class Params:
        target_post = Trait(
            state="target_post",
            post=Iterator(Post.objects.filter(publish_date__isnull=False)),
        )
        target_comment = Trait(
            state="target_comment",
            comment=Iterator(Comment.objects.filter(post__publish_date__isnull=False)),
        )

    owner = Iterator(User.objects.filter(is_superuser=False))
    type = Faker(
        "word",
        ext_word_list=[Reaction.ReactionType.LIKE, Reaction.ReactionType.DISLIKE],
    )
    post = None
    comment = None

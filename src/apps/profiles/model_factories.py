from factory import Faker, post_generation
from factory.django import DjangoModelFactory

from .models import Profile


# Foreign key handled by UserFactory
class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile

    pic = ""
    bio = Faker("text", max_nb_chars=300)

    @post_generation
    def followers(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        # Add the iterable of followers using bulk addition
        self.followers.add(*extracted)

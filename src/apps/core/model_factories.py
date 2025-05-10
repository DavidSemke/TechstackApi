from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from factory import Faker, RelatedFactory
from factory.django import DjangoModelFactory, Password, mute_signals

from ..profiles.model_factories import ProfileFactory

User = get_user_model()


# The post_save signal triggers profile creation
# Ignore the signal here to allow use of ProfileFactory
@mute_signals(post_save)
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Faker("name")
    password = Password("password")
    email = Faker("email")
    profile = RelatedFactory(ProfileFactory, factory_related_name="user")

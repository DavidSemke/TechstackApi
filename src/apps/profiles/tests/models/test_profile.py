from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from ...models import Profile


class ProfileModelTest(TestCase):
    def test_profile_created_with_user(self):
        # If the User model is used directly for user creation,
        # creation of default groups is required (currently only 'commenter').
        Group.objects.create(name="commenter")
        User = get_user_model()

        # UserFactory disables the signal used to create a profile
        # Use the User model here instead
        user = User.objects.create(username="username", password="password")

        try:
            Profile.objects.get(owner=user)
        except Profile.DoesNotExist:
            self.fail("Profile was not created with user")

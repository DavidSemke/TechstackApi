from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Profile


class ProfileModelTest(TestCase):
    def test_profile_created_with_user(self):
        User = get_user_model()

        # UserFactory disables the signal used to create a profile
        # Use the User model here instead
        user = User.objects.create(username="username", password="password")

        try:
            Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            self.fail("Profile was not created with user")

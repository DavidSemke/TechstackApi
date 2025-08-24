from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ....core.model_factories import UserFactory
from ....core.tests import utils as test_utils


class ProfileListTest(APITestCase):
    def setUp(self):
        # Creating a user automatically creates a profile
        self.user1 = UserFactory()
        self.url = reverse("profile-list")
        return super().setUp()

    def test_get_guest(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        profile_id = test_utils.last_url_pk(res.data["results"][0]["url"])
        self.assertEqual(self.user1.profile.id, profile_id)

    def test_post_put_patch_delete_guest(self):
        methods = ["post", "put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.url)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # POST = 403 because profiles are automatically created for users and each user is
    # limited to one profile.
    def test_post_login(self):
        test_utils.jwt_login(self.client, self.user1.username)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.post(self.url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_patch_delete_login(self):
        test_utils.jwt_login(self.client, self.user1.username)

        methods = ["put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.url)

            self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

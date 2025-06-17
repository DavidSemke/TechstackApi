from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ....core.model_factories import UserFactory
from ....core.tests import utils as test_utils


class ProfileDetailTest(APITestCase):
    def setUp(self):
        self.user1 = UserFactory()
        self.url = reverse("profile-detail", kwargs={"pk": self.user1.profile.id})
        return super().setUp()

    def test_get_guest(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        profile_id = test_utils.last_url_pk(res.data["url"])
        self.assertEqual(self.user1.profile.id, profile_id)

    def test_post_put_patch_delete_guest(self):
        methods = ["post", "put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.url)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_login(self):
        user2 = UserFactory()

        tokens = self.client.post(
            reverse("jwt-create"), {"username": user2.username, "password": "password"}
        ).json()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.post(self.url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_patch_delete_login(self):
        user2 = UserFactory()

        tokens = self.client.post(
            reverse("jwt-create"), {"username": user2.username, "password": "password"}
        ).json()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        methods = ["put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.url)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_login_profile_owner(self):
        tokens = self.client.post(
            reverse("jwt-create"),
            {"username": self.user1.username, "password": "password"},
        ).json()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.post(self.url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_login_profile_owner(self):
        tokens = self.client.post(
            reverse("jwt-create"),
            {"username": self.user1.username, "password": "password"},
        ).json()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        profile1 = self.user1.profile
        new_bio = "put"
        self.assertNotEqual(profile1.bio, new_bio)

        res = self.client.put(
            self.url,
            {"bio": new_bio},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        profile1.refresh_from_db()
        self.assertEqual(profile1.bio, new_bio)

    def test_patch_login_profile_owner(self):
        tokens = self.client.post(
            reverse("jwt-create"),
            {"username": self.user1.username, "password": "password"},
        ).json()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        profile1 = self.user1.profile
        new_bio = "patch"
        self.assertNotEqual(profile1.bio, new_bio)

        res = self.client.patch(
            self.url,
            {"bio": new_bio},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        profile1.refresh_from_db()
        self.assertEqual(profile1.bio, new_bio)

    def test_delete_login_profile_owner(self):
        tokens = self.client.post(
            reverse("jwt-create"),
            {"username": self.user1.username, "password": "password"},
        ).json()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.delete(self.url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

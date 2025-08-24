from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ....core import model_factories as core_factories
from ....core.tests import utils as test_utils


class GroupDetailTest(APITestCase):
    def get_url(self, group_id):
        return reverse("group-detail", kwargs={"pk": group_id})

    def setUp(self):
        # If the User model is used directly for user creation,
        # creation of default groups is required (currently only 'commenter').
        self.group = Group.objects.create(name="commenter")
        self.group_url = self.get_url(self.group.id)
        return super().setUp()

    def test_get_post_put_patch_delete_guest(self):
        methods = ["get", "post", "put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.group_url)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_put_patch_delete_login(self):
        user1 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user1.username)

        methods = ["get", "put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.group_url)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_login(self):
        user1 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user1.username)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.post(self.group_url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_login_admin(self):
        User = get_user_model()
        user2 = User.objects.create_superuser(
            username="test_admin",
            password="password",
        )
        test_utils.jwt_login(self.client, user2.username)

        res = self.client.get(self.group_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        group_id = res.data["id"]
        self.assertEqual(self.group.id, group_id)

    def test_post_login_admin(self):
        User = get_user_model()
        user2 = User.objects.create_superuser(
            username="test_admin",
            password="password",
        )
        test_utils.jwt_login(self.client, user2.username)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.post(self.group_url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_login_admin(self):
        User = get_user_model()
        user2 = User.objects.create_superuser(
            username="test_admin",
            password="password",
        )
        test_utils.jwt_login(self.client, user2.username)

        new_name = "better_tester"
        self.assertNotEqual(self.group.name, new_name)
        res = self.client.put(self.group_url, {"name": new_name})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.group.refresh_from_db()
        self.assertEqual(self.group.name, new_name)

    def test_patch_login_admin(self):
        User = get_user_model()
        user2 = User.objects.create_superuser(
            username="test_admin",
            password="password",
        )
        test_utils.jwt_login(self.client, user2.username)

        new_name = "better_tester"
        self.assertNotEqual(self.group.name, new_name)
        res = self.client.patch(self.group_url, {"name": new_name})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.group.refresh_from_db()
        self.assertEqual(self.group.name, new_name)

    def test_delete_login_admin(self):
        User = get_user_model()
        user2 = User.objects.create_superuser(
            username="test_admin",
            password="password",
        )
        test_utils.jwt_login(self.client, user2.username)

        res = self.client.delete(self.group_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Group.DoesNotExist):
            self.group.refresh_from_db()

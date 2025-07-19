from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ....core import model_factories as core_factories
from ....core.tests import utils as test_utils


class GroupListTest(APITestCase):
    def setUp(self):
        self.group = Group.objects.create(name="commenter")
        self.url = reverse("group-list")
        return super().setUp()

    def test_get_post_put_patch_delete_guest(self):
        methods = ["get", "post", "put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.url)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_post_login(self):
        user1 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user1.username)

        methods = ["get", "post"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.url)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_patch_delete_login(self):
        user1 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user1.username)

        methods = ["put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.url)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_login_admin(self):
        User = get_user_model()
        user2 = User.objects.create_superuser(
            username="test_admin",
            password="password",
        )
        test_utils.jwt_login(self.client, user2.username)

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        group_id = test_utils.last_url_pk(res.data[0]["url"])
        self.assertEqual(self.group.id, group_id)

    def test_post_login_admin(self):
        User = get_user_model()
        user2 = User.objects.create_superuser(
            username="test_admin",
            password="password",
        )
        test_utils.jwt_login(self.client, user2.username)

        group_name = "better_tester"
        self.assertFalse(Group.objects.filter(name=group_name).exists())
        res = self.client.post(self.url, {"name": group_name})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Group.objects.filter(name=group_name).exists())

    def test_put_patch_delete_login_admin(self):
        User = get_user_model()
        user2 = User.objects.create_superuser(
            username="test_admin",
            password="password",
        )
        test_utils.jwt_login(self.client, user2.username)

        methods = ["put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.url)

            self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

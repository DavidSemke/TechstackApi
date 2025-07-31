from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ....core import model_factories as core_factories
from ....core.tests import utils as test_utils


class UserDetailTest(APITestCase):
    def get_url(self, user_id):
        return reverse("user-detail", kwargs={"pk": user_id})

    def setUp(self):
        # If the User model is used directly for user creation,
        # creation of default groups is required (currently only 'commenter').
        self.comment_group = Group.objects.create(name="commenter")
        self.user1 = core_factories.UserFactory()
        self.user_url = self.get_url(self.user1.id)
        return super().setUp()

    def test_get_post_put_patch_delete_guest(self):
        methods = ["get", "post", "put", "patch", "delete"]

        for method in methods:
            method_func = getattr(self.client, method)

            with self.assertLogs("django.request", level="WARNING"):
                res = method_func(self.user_url)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # The UserViewSet 'me' action should be used instead of default detail url
    def test_get_login(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.get(self.user_url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_login(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.post(self.user_url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_login(self):
        test_utils.jwt_login(self.client, self.user1.username)

        new_username = "better_tester"
        self.assertNotEqual(self.user1.username, new_username)
        res = self.client.put(self.user_url, {"username": new_username})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, new_username)

    def test_patch_login(self):
        test_utils.jwt_login(self.client, self.user1.username)

        new_username = "better_tester"
        self.assertNotEqual(self.user1.username, new_username)
        res = self.client.patch(self.user_url, {"username": new_username})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, new_username)

    def test_delete_login(self):
        test_utils.jwt_login(self.client, self.user1.username)

        res = self.client.delete(self.user_url, {"current_password": "password"})
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        User = get_user_model()

        with self.assertRaises(User.DoesNotExist):
            self.user1.refresh_from_db()

    def test_get_login_admin(self):
        User = get_user_model()
        user2 = User.objects.create_superuser(
            username="test_admin",
            password="password",
        )
        test_utils.jwt_login(self.client, user2.username)

        res = self.client.get(self.user_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user1.id, res.data["id"])

    def test_put_login_admin(self):
        User = get_user_model()
        user2 = User.objects.create_superuser(
            username="test_admin",
            password="password",
        )
        test_utils.jwt_login(self.client, user2.username)

        new_username = "better_tester"
        self.assertNotEqual(self.user1.username, new_username)
        res = self.client.put(self.user_url, {"username": new_username})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, new_username)

    def test_patch_login_admin(self):
        User = get_user_model()
        user2 = User.objects.create_superuser(
            username="test_admin",
            password="password",
        )
        test_utils.jwt_login(self.client, user2.username)

        new_username = "better_tester"
        self.assertNotEqual(self.user1.username, new_username)
        res = self.client.patch(self.user_url, {"username": new_username})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, new_username)

    def test_delete_login_admin(self):
        User = get_user_model()
        user2 = User.objects.create_superuser(
            username="test_admin",
            password="password",
        )
        test_utils.jwt_login(self.client, user2.username)

        res = self.client.delete(self.user_url, {"current_password": "password"})
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(User.DoesNotExist):
            self.user1.refresh_from_db()

    def test_get_login_moderator(self):
        user2 = core_factories.UserFactory()
        mod_group = Group.objects.create(name="moderator")
        user2.groups.add(mod_group)
        test_utils.jwt_login(self.client, user2.username)

        res = self.client.get(self.user_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user1.id, res.data["id"])

    def test_put_login_moderator(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)

        mod_group = Group.objects.create(name="moderator")
        user2.groups.add(mod_group)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.put(self.user_url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_login_moderator(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)

        mod_group = Group.objects.create(name="moderator")
        user2.groups.add(mod_group)
        self.user1.groups.add(self.comment_group)

        groups = list(self.user1.groups.all())
        self.assertEqual(len(groups), 1)
        self.assertIn(self.comment_group, groups)

        author_group = Group.objects.create(name="author")
        res = self.client.patch(self.user_url, {"groups": ["author"]})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user1.refresh_from_db()
        groups = list(self.user1.groups.all())
        self.assertEqual(len(groups), 1)
        self.assertIn(author_group, groups)

    def test_patch_login_moderator_making_moderator(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)

        mod_group = Group.objects.create(name="moderator")
        user2.groups.add(mod_group)
        self.user1.groups.add(self.comment_group)

        groups = list(self.user1.groups.all())
        self.assertEqual(len(groups), 1)
        self.assertIn(self.comment_group, groups)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.patch(self.user_url, {"groups": ["moderator"]})

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_login_moderator_removing_moderator(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)

        mod_group = Group.objects.create(name="moderator")
        user2.groups.add(mod_group)
        self.user1.groups.add(mod_group)

        groups = list(self.user1.groups.all())
        self.assertEqual(len(groups), 1)
        self.assertIn(mod_group, groups)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.patch(self.user_url, {"groups": []})

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_login_moderator(self):
        user2 = core_factories.UserFactory()
        test_utils.jwt_login(self.client, user2.username)

        mod_group = Group.objects.create(name="moderator")
        user2.groups.add(mod_group)

        with self.assertLogs("django.request", level="WARNING"):
            res = self.client.delete(self.user_url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

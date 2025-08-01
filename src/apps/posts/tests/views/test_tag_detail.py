from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ....core import model_factories as core_factories
from ....core.tests import utils as test_utils
from ... import model_factories as posts_factories
from ... import models as posts_models


class TagDetailTest(APITestCase):
    def get_url(self, tag_id):
        return reverse("tag-detail", kwargs={"pk": tag_id})

    def setUp(self):
        self.user1 = core_factories.UserFactory()
        self.author_group = Group.objects.create(name="author")
        self.user1.groups.add(self.author_group)
        self.tag = posts_factories.TagFactory()
        self.tag_url = self.get_url(self.tag.id)
        return super().setUp()

    # def test_get_guest(self):
    #     res = self.client.get(self.tag_url)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     tag_id = test_utils.last_url_pk(res.data["url"])
    #     self.assertEqual(self.tag.id, tag_id)

    # def test_post_put_patch_delete_guest(self):
    #     methods = ["post", "put", "patch", "delete"]

    #     for method in methods:
    #         method_func = getattr(self.client, method)

    #         with self.assertLogs("django.request", level="WARNING"):
    #             res = method_func(self.tag_url)

    #         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_post_login(self):
    #     test_utils.jwt_login(self.client, self.user1.username)

    #     with self.assertLogs("django.request", level="WARNING"):
    #         res = self.client.post(self.tag_url)

    #     self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # def test_put_patch_delete_login(self):
    #     user2 = core_factories.UserFactory()
    #     test_utils.jwt_login(self.client, user2.username)

    #     methods = ["put", "patch", "delete"]

    #     for method in methods:
    #         method_func = getattr(self.client, method)

    #         with self.assertLogs("django.request", level="WARNING"):
    #             res = method_func(self.tag_url)

    #         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_login_moderator(self):
        user2 = core_factories.UserFactory()
        mod_group = Group.objects.create(name="moderator")
        user2.groups.add(mod_group)
        test_utils.jwt_login(self.client, user2.username)

        new_title = "new-title"
        self.assertNotEqual(new_title, self.tag.title)
        res = self.client.put(self.tag_url, {"title": new_title})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.tag.refresh_from_db()
        self.assertEqual(new_title, self.tag.title)

    def test_patch_login_moderator(self):
        user2 = core_factories.UserFactory()
        mod_group = Group.objects.create(name="moderator")
        user2.groups.add(mod_group)
        test_utils.jwt_login(self.client, user2.username)

        new_title = "new-title"
        self.assertNotEqual(new_title, self.tag.title)
        res = self.client.patch(self.tag_url, {"title": new_title})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.tag.refresh_from_db()
        self.assertEqual(new_title, self.tag.title)

    def test_delete_login_moderator(self):
        user2 = core_factories.UserFactory()
        mod_group = Group.objects.create(name="moderator")
        user2.groups.add(mod_group)
        test_utils.jwt_login(self.client, user2.username)

        res = self.client.delete(self.tag_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(posts_models.Tag.DoesNotExist):
            self.tag.refresh_from_db()

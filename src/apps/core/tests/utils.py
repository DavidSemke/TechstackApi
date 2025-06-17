from django.urls import reverse
from rest_framework.test import APIClient


def last_url_pk(url: str) -> int:
    return int(url.strip("/").split("/")[-1])


def jwt_login(client: APIClient, username: str):
    tokens = client.post(
        reverse("jwt-create"), {"username": username, "password": "password"}
    ).json()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

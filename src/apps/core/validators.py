import os

import requests
from django.core.exceptions import ValidationError


def validate_image_url(url):
    image_exts = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    ext = os.path.splitext(url)[1].lower()

    if ext not in image_exts:
        raise ValidationError("URL does not have a valid image file extension.")

    try:
        res = requests.head(url, allow_redirects=True, timeout=5)
    except requests.RequestException:
        raise ValidationError("Unable to reach the URL.")

    content_type = res.headers["content-type"]

    if not content_type.startswith("image/"):
        raise ValidationError("URL does not point to an image.")

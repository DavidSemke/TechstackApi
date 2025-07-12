import requests


def rand_image_url(dims=(200, 200)):
    width, height = dims
    url = f"https://picsum.photos/{width}/{height}"
    res = requests.get(url, allow_redirects=True, timeout=5)
    return res.url

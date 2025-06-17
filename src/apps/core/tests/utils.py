def last_url_pk(url: str) -> int:
    return int(url.strip("/").split("/")[-1])

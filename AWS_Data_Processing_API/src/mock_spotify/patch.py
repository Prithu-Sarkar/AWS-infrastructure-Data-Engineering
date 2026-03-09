import requests
import random
import time
from urllib.parse import urlparse, parse_qs
from .responses import token_response, new_releases_response, album_tracks_response
import json

class MockResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status
        self.content = json.dumps(payload).encode()

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

REAL_GET = requests.get
REAL_POST = requests.post

def mocked_post(url, *args, **kwargs):
    if "accounts.spotify.com/api/token" in url:
        time.sleep(random.uniform(0.05, 0.2))
        return MockResponse(token_response())
    return REAL_POST(url, *args, **kwargs)

def mocked_get(url, *args, **kwargs):
    if "api.spotify.com/v1/browse/new-releases" in url:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        offset = int(qs.get("offset", [0])[0])
        limit = int(qs.get("limit", [20])[0])
        if random.random() < 0.05:
            return MockResponse({"error": {"status": 429, "message": "Too Many Requests"}}, status=429)
        time.sleep(random.uniform(0.05, 0.2))
        return MockResponse(new_releases_response(offset=offset, limit=limit))
    if "/v1/albums/" in url and "/tracks" in url:
        parsed = urlparse(url)
        # Path example: /v1/albums/<album_id>/tracks
        parts = parsed.path.strip("/").split("/")
        album_id = parts[2] if len(parts) >= 3 else ""
        qs = parse_qs(parsed.query)
        offset = int(qs.get("offset", [0])[0])
        limit = int(qs.get("limit", [20])[0])
        time.sleep(random.uniform(0.05, 0.2))
        return MockResponse(album_tracks_response(album_id, offset=offset, limit=limit))
    return REAL_GET(url, *args, **kwargs)

def enable():
    requests.post = mocked_post
    requests.get = mocked_get

from pathlib import Path
import json

DATA = Path(__file__).parent / "data"

# -----------------------------
# Load all albums
# -----------------------------
def load_all_new_releases():
    """Return a list of all albums as stored in JSON"""
    with open(DATA / "all_new_releases.json") as f:
        return json.load(f)["albums"]

def load_all_album_tracks(album_id):
    """Return list of tracks for a given album_id. 
    Ensures album_id is treated as a string to match main.py IDs.
    Returns empty list if album_id not found.
    """
    with open(DATA / "all_album_tracks.json") as f:
        data = json.load(f)
        return data.get(str(album_id), [])

# -----------------------------
# Mock token
# -----------------------------
def token_response():
    return {
        "access_token": "mock_access_token",
        "token_type": "Bearer",
        "expires_in": 3600
    }

# -----------------------------
# Mock new releases endpoint
# -----------------------------
def new_releases_response(offset=0, limit=20):
    all_albums = load_all_new_releases()
    slice_ = all_albums[offset:offset+limit]
    next_offset = offset + limit
    prev_offset = offset - limit
    return {
        "albums": {
            "href": f"https://api.spotify.com/v1/browse/new-releases?offset={offset}&limit={limit}",
            "items": slice_,
            "limit": limit,
            "next": f"https://api.spotify.com/v1/browse/new-releases?offset={next_offset}&limit={limit}" if next_offset < len(all_albums) else None,
            "offset": offset,
            "previous": f"https://api.spotify.com/v1/browse/new-releases?offset={prev_offset}&limit={limit}" if prev_offset >= 0 else None,
            "total": len(all_albums)
        }
    }

# -----------------------------
# Mock album tracks endpoint
# -----------------------------
def album_tracks_response(album_id, offset=0, limit=20):
    all_tracks = load_all_album_tracks(album_id)
    slice_ = all_tracks[offset:offset+limit]
    next_offset = offset + limit
    prev_offset = offset - limit
    return {
        "href": f"https://api.spotify.com/v1/albums/{album_id}/tracks?offset={offset}&limit={limit}",
        "items": slice_,
        "limit": limit,
        "next": f"https://api.spotify.com/v1/albums/{album_id}/tracks?offset={next_offset}&limit={limit}" if next_offset < len(all_tracks) else None,
        "offset": offset,
        "previous": f"https://api.spotify.com/v1/albums/{album_id}/tracks?offset={prev_offset}&limit={limit}" if prev_offset >= 0 else None,
        "total": len(all_tracks)
    }

# -----------------------------
# Utility to ensure all album IDs have tracks
# -----------------------------
def ensure_all_tracks_exist():
    """Adds empty track lists for any album ID missing in all_album_tracks.json"""
    all_albums = load_all_new_releases()
    with open(DATA / "all_album_tracks.json") as f:
        album_tracks_data = json.load(f)

    updated = False
    for album in all_albums:
        album_id = str(album["id"])
        if album_id not in album_tracks_data:
            album_tracks_data[album_id] = []
            updated = True

    if updated:
        with open(DATA / "all_album_tracks.json", "w") as f:
            json.dump(album_tracks_data, f, indent=2)

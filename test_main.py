import unittest
from main import get_spotify_client
from dotenv import load_dotenv

class TestSpotifyClient(unittest.TestCase):
    def test_auth(self):
        load_dotenv()
        sp = get_spotify_client()
        birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'
        results = sp.artist_albums(birdy_uri, album_type='album')
        albums = results['items']
        while results['next']:
            results = sp.next(results)
            albums.extend(results['items'])

        for album in albums:
            print(album['name'])

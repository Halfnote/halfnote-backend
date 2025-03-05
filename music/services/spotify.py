import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Optional, Dict
import logging
import os

logger = logging.getLogger(__name__)

class SpotifyClient:
    def __init__(self):
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
        )
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def search_album(self, title: str, artist: Optional[str] = None) -> Optional[Dict]:
        try:
            query = f"album:{title}"
            if artist:
                query += f" artist:{artist}"
            
            results = self.sp.search(q=query, type='album', limit=1)
            
            if results['albums']['items']:
                album = results['albums']['items'][0]
                album_id = album['id']
                
                # Get full album details including genres
                album_details = self.sp.album(album_id)
                
                return {
                    'spotify_url': album['external_urls']['spotify'],
                    'spotify_embed_url': f"https://open.spotify.com/embed/album/{album_id}",
                    'cover_art_url': album['images'][0]['url'] if album['images'] else None,
                    'genres': album_details.get('genres', [])
                }
            return None
        except Exception as e:
            logger.error(f"Spotify search error: {str(e)}")
            return None

    def search_track(self, title: str, artist: Optional[str] = None) -> Optional[Dict]:
        try:
            query = f"track:{title}"
            if artist:
                query += f" artist:{artist}"
            
            results = self.sp.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                track_id = track['id']
                
                # Get album genres from the track's album
                album_details = self.sp.album(track['album']['id'])
                
                return {
                    'spotify_url': track['external_urls']['spotify'],
                    'spotify_embed_url': f"https://open.spotify.com/embed/track/{track_id}",
                    'cover_art_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'genres': album_details.get('genres', [])
                }
            return None
        except Exception as e:
            logger.error(f"Spotify track search error: {str(e)}")
            return None 
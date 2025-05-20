import requests
import logging
import time
from typing import List, Dict, Optional
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ExternalMusicService:
    BASE_URL = "https://api.discogs.com"
    
    def __init__(self):
        self.user_agent = "BoomboxdApp/1.0 +http://boomboxd.com"
        self.consumer_key = settings.DISCOGS_CONSUMER_KEY
        self.consumer_secret = settings.DISCOGS_CONSUMER_SECRET
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum seconds between requests
        
    def _make_request(self, endpoint, params=None):
        """Make a rate-limited request to Discogs API"""
        # Rate limiting - ensure minimum time between requests
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        
        if params is None:
            params = {}
            
        # Add authentication
        headers = {'User-Agent': self.user_agent}
        params.update({
            'key': self.consumer_key,
            'secret': self.consumer_secret
        })
        
        url = f"{self.BASE_URL}/{endpoint}"
        logger.info(f"Making Discogs API request to: {url}")
        
        try:
            response = requests.get(url, params=params, headers=headers)
            self.last_request_time = time.time()
            
            if response.status_code != 200:
                logger.error(f"Discogs API error: {response.status_code} - {response.text}")
                return None
                
            return response.json()
        except Exception as e:
            logger.error(f"Error making Discogs API request: {str(e)}")
            return None

    def search_discogs(self, query, cache_key):
        """Search for albums on Discogs with caching"""
        logger.info(f"Searching Discogs for query: {query}")
        
        cached_results = cache.get(cache_key)
        if cached_results:
            logger.info(f"Returning cached results for {query}")
            return cached_results

        try:
            params = {
                'type': 'master',  # Use master releases
                'format': 'album',  # Only albums
                'per_page': 10     # Limit results
            }
            
            # If query contains " - ", split into artist and title
            if ' - ' in query:
                artist, title = query.split(' - ', 1)
                params['artist'] = artist.strip()
                params['release_title'] = title.strip()
            else:
                params['q'] = query
            
            data = self._make_request("database/search", params)
            if not data:
                return []
                
            formatted_results = []
            for item in data.get('results', []):
                try:
                    # Extract artist from the title if it contains " - "
                    item_artist = item.get('artist', '')
                    if not item_artist and ' - ' in item.get('title', ''):
                        parts = item.get('title', '').split(' - ', 1)
                        item_artist = parts[0].strip()
                    
                    formatted_results.append({
                        'title': item.get('title', '').split(' - ')[-1].strip(),
                        'artist': item_artist,
                        'year': item.get('year'),
                        'genres': item.get('genre', []),
                        'styles': item.get('style', []),
                        'cover_image': item.get('thumb', item.get('cover_image')),
                        'discogs_id': str(item.get('id')),
                        'discogs_url': f"https://www.discogs.com/master/{item.get('id')}",
                        'master_id': item.get('master_id'),
                        'master_url': item.get('master_url'),
                        'country': item.get('country')
                    })
                except Exception as e:
                    logger.error(f"Error processing Discogs result: {str(e)}", exc_info=True)
                    continue
            
            logger.info(f"Formatted {len(formatted_results)} results")
            cache.set(cache_key, formatted_results, timeout=3600)  # Cache for 1 hour
            return formatted_results
            
        except Exception as e:
            logger.error(f"Discogs API error: {str(e)}", exc_info=True)
            return []

    def get_spotify_embed(self, query, cache_key):
        """Get Spotify embed URL for an album"""
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        try:
            results = self.spotify.search(query, type='album', limit=1)
            if not results['albums']['items']:
                return None
                
            album = results['albums']['items'][0]
            result = {
                'spotify_url': album['external_urls']['spotify'],
                'spotify_embed_url': f"https://open.spotify.com/embed/album/{album['id']}"
            }
            
            cache.set(cache_key, result, timeout=3600)  # Cache for 1 hour
            return result
            
        except Exception as e:
            logger.error(f"Spotify API error getting embed: {str(e)}")
            return None

    def search_spotify(self, query, cache_key):
        """Search for albums on Spotify with caching"""
        cached_results = cache.get(cache_key)
        if cached_results:
            return cached_results

        try:
            results = self.spotify.search(query, type='album', limit=10)
            formatted_results = []
            
            for album in results['albums']['items']:
                formatted_results.append({
                    'title': album['name'],
                    'artist': album['artists'][0]['name'] if album['artists'] else 'Unknown Artist',
                    'cover_image': album['images'][0]['url'] if album['images'] else None,
                    'spotify_id': album['id'],
                    'release_date': album['release_date'],
                })
            
            cache.set(cache_key, formatted_results, timeout=3600)  # Cache for 1 hour
            return formatted_results
            
        except Exception as e:
            logger.error(f"Spotify API error: {str(e)}")
            return []

    def search_spotify_matches(self, query, cache_key, limit=5):
        """Search for potential Spotify matches for an album"""
        cached_results = cache.get(cache_key)
        if cached_results:
            return cached_results

        try:
            results = self.spotify.search(query, type='album', limit=limit)
            matches = []
            
            for album in results['albums']['items']:
                matches.append({
                    'spotify_id': album['id'],
                    'title': album['name'],
                    'artist': album['artists'][0]['name'],
                    'release_date': album['release_date'],
                    'total_tracks': album['total_tracks'],
                    'images': album['images'],
                    'spotify_url': album['external_urls']['spotify'],
                    'spotify_embed_url': f"https://open.spotify.com/embed/album/{album['id']}"
                })
            
            cache.set(cache_key, matches, timeout=3600)  # Cache for 1 hour
            return matches
            
        except Exception as e:
            logger.error(f"Spotify API error: {str(e)}")
            return []

    def verify_spotify_album(self, spotify_id):
        """Verify that a Spotify album ID exists"""
        try:
            album = self.spotify.album(spotify_id)
            return bool(album)
        except Exception as e:
            logger.error(f"Error verifying Spotify album {spotify_id}: {str(e)}")
            return False 
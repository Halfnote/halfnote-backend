import requests
import logging
import time
from typing import List, Dict, Optional
from django.conf import settings

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
    
    def search_discogs(self, query):
        """Search for albums on Discogs"""
        logger.info(f"Searching Discogs for query: {query}")
        
        try:
            params = {
                'type': 'master',  # Just master releases
                'format': 'album', 
                'per_page': 10     
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
                        'cover_image': item.get('cover_image', ''),
                        'discogs_id': str(item.get('id'))
                    })
                except Exception as e:
                    logger.error(f"Error processing Discogs result: {str(e)}")
                    continue
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Discogs API error: {str(e)}")
            return []

    def get_album_details(self, discogs_id):
        """Get detailed information about an album from Discogs"""
        logger.info(f"Fetching album details for Discogs ID: {discogs_id}")
        
        try:
            # For master releases, use the masters endpoint
            data = self._make_request(f"masters/{discogs_id}")
            
            if not data:
                # If not found as a master, try the release endpoint
                data = self._make_request(f"releases/{discogs_id}")
            
            if not data:
                logger.error(f"Album not found on Discogs: {discogs_id}")
                return None
            
            # Get the main artist name
            artist_name = "Unknown Artist"
            if 'artists' in data and data['artists']:
                artist_name = data['artists'][0].get('name', "Unknown Artist")
            
            # Format the album data
            album_data = {
                'title': data.get('title', ''),
                'artist': artist_name,
                'year': data.get('year', ''),
                'genres': data.get('genres', []),
                'styles': data.get('styles', []),
                'cover_image': '',
                'discogs_id': discogs_id,
                'tracklist': []
            }
            
            # Get the cover image
            if 'images' in data and data['images']:
                primary_images = [img for img in data['images'] if img.get('type') == 'primary']
                if primary_images:
                    album_data['cover_image'] = primary_images[0].get('uri', '')
                else:
                    album_data['cover_image'] = data['images'][0].get('uri', '')
            
            # Get the tracklist
            if 'tracklist' in data:
                album_data['tracklist'] = [
                    {
                        'position': track.get('position', ''),
                        'title': track.get('title', ''),
                        'duration': track.get('duration', '')
                    }
                    for track in data['tracklist']
                    if track.get('type_') != 'heading'  # Skip headings
                ]
            
            return album_data
            
        except Exception as e:
            logger.error(f"Error fetching album details from Discogs: {str(e)}")
            return None 
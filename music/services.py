import requests
import logging
import time
from typing import List, Dict, Optional, Any
from django.conf import settings

logger = logging.getLogger(__name__)

class ExternalMusicService:
    def __init__(self):
        self.base_url = settings.DISCOGS_API_URL
        self.consumer_key = settings.DISCOGS_CONSUMER_KEY
        self.consumer_secret = settings.DISCOGS_CONSUMER_SECRET
        self.token = settings.DISCOGS_TOKEN
        self.user_agent = "HalfnoteApp/1.0 +http://halfnote.com"
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum seconds between requests
        
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the Discogs API
        """
        headers = {
            'User-Agent': 'HalfnoteApp/1.0'
        }

        # Add authentication via query parameters (simpler approach)
        if params is None:
            params = {}
        params.update({
            'key': self.consumer_key,
            'secret': self.consumer_secret
        })

        url = f"{self.base_url}/{endpoint}"
        logger.info(f"Making Discogs API request to: {url}")

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Discogs API: {str(e)}")
            raise
    
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
            # First try to get the master release
            master_data = self._make_request(f"masters/{discogs_id}")
            
            if master_data:
                # If we found a master release, get the main release
                main_release_id = master_data.get('main_release')
                if main_release_id:
                    release_data = self._make_request(f"releases/{main_release_id}")
                else:
                    release_data = None
            else:
                # If not found as a master, try the release endpoint
                release_data = self._make_request(f"releases/{discogs_id}")
                master_data = None
            
            if not release_data and not master_data:
                logger.error(f"Album not found on Discogs: {discogs_id}")
                return None
            
            # Use release data if available, otherwise use master data
            data = release_data or master_data
            
            # Get the main artist name
            artist_name = "Unknown Artist"
            if 'artists' in data and data['artists']:
                artist_name = data['artists'][0].get('name', "Unknown Artist")
            
            # Get the tracklist with more details
            tracklist = []
            if 'tracklist' in data:
                for track in data['tracklist']:
                    if track.get('type_') != 'heading':  # Skip headings
                        tracklist.append({
                            'position': track.get('position', ''),
                            'title': track.get('title', ''),
                            'duration': track.get('duration', ''),
                            'artists': track.get('artists', []),
                            'extraartists': track.get('extraartists', [])
                        })
            
            # Get credits
            credits = []
            if 'extraartists' in data:
                for artist in data['extraartists']:
                    credits.append({
                        'name': artist.get('name', ''),
                        'role': artist.get('role', ''),
                        'id': artist.get('id', '')
                    })
            
            album_data = {
                'title': data.get('title', ''),
                'artist': artist_name,
                'year': data.get('year', ''),
                'genres': data.get('genres', []),
                'styles': data.get('styles', []),
                'cover_image': '',
                'discogs_id': discogs_id,
                'tracklist': tracklist,
                'credits': credits
            }
            
            # Get the cover image
            if 'images' in data and data['images']:
                primary_images = [img for img in data['images'] if img.get('type') == 'primary']
                if primary_images:
                    album_data['cover_image'] = primary_images[0].get('uri', '')
                else:
                    album_data['cover_image'] = data['images'][0].get('uri', '')
            
            return album_data
        except Exception as e:
            logger.error(f"Error fetching album details from Discogs: {str(e)}")
            return None 
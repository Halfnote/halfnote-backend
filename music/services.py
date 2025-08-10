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
    
    def _clean_artist_name(self, artist_name: str) -> str:
        """
        Clean up artist names by removing Discogs disambiguation numbers like (2), (3), etc.
        But keep meaningful parentheses like band names: "Earth, Wind & Fire"
        """
        if not artist_name:
            return artist_name
            
        # Remove disambiguation numbers: (2), (3), (10), etc.
        # This regex matches ( followed by digits followed by )
        import re
        cleaned = re.sub(r'\s*\(\d+\)$', '', artist_name).strip()
        return cleaned if cleaned else artist_name
        
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
            response = requests.get(url, params=params, headers=headers, timeout=(2, 10))
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
                        'artist': self._clean_artist_name(item_artist),
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
                raw_artist_name = data['artists'][0].get('name', "Unknown Artist")
                artist_name = self._clean_artist_name(raw_artist_name)
            
            # Get the tracklist with more details
            tracklist = []
            if 'tracklist' in data:
                for track in data['tracklist']:
                    if track.get('type_') != 'heading':  # Skip headings
                        # Clean artist names in tracklist
                        artists = track.get('artists', [])
                        cleaned_artists = []
                        for artist in artists:
                            if isinstance(artist, dict) and 'name' in artist:
                                cleaned_name = self._clean_artist_name(artist['name'])
                                cleaned_artist = artist.copy()
                                cleaned_artist['name'] = cleaned_name
                                cleaned_artists.append(cleaned_artist)
                            elif isinstance(artist, str):
                                cleaned_artists.append(self._clean_artist_name(artist))
                            else:
                                cleaned_artists.append(artist)
                        
                        # Clean extraartists names as well
                        extraartists = track.get('extraartists', [])
                        cleaned_extraartists = []
                        for artist in extraartists:
                            if isinstance(artist, dict) and 'name' in artist:
                                cleaned_name = self._clean_artist_name(artist['name'])
                                cleaned_artist = artist.copy()
                                cleaned_artist['name'] = cleaned_name
                                cleaned_extraartists.append(cleaned_artist)
                            else:
                                cleaned_extraartists.append(artist)
                        
                        tracklist.append({
                            'position': track.get('position', ''),
                            'title': track.get('title', ''),
                            'duration': track.get('duration', ''),
                            'artists': cleaned_artists,
                            'extraartists': cleaned_extraartists
                        })
            
            # Get credits with cleaned artist names
            credits = []
            if 'extraartists' in data:
                for artist in data['extraartists']:
                    credits.append({
                        'name': self._clean_artist_name(artist.get('name', '')),
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
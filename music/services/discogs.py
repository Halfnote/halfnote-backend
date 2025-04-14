import requests
import logging
import time
from typing import List, Dict, Optional
import re
from datetime import datetime
import os
from django.conf import settings

logger = logging.getLogger(__name__)

class DiscogsClient:
    BASE_URL = "https://api.discogs.com"
    
    # Add a genre mapping dictionary to map Discogs genres to our supported genres
    GENRE_MAPPING = {
        # Rock and related genres
        'rock': 'Rock',
        'alternative rock': 'Rock',
        'hard rock': 'Rock',
        'indie rock': 'Rock',
        'classic rock': 'Rock',
        'punk': 'Rock',
        'metal': 'Rock',
        'grunge': 'Rock',
        
        # Pop and related genres
        'pop': 'Pop',
        'synth-pop': 'Pop',
        'disco': 'Pop',
        'dance': 'Pop',
        'electropop': 'Pop',
        'britpop': 'Pop',
        
        # Electronic and related genres
        'electronic': 'Electronic',
        'techno': 'Electronic',
        'house': 'Electronic',
        'trance': 'Electronic',
        'ambient': 'Electronic',
        'downtempo': 'Electronic',
        'dubstep': 'Electronic',
        'edm': 'Electronic',
        
        # Hip-hop and related genres
        'hip hop': 'Hip-hop',
        'hip-hop': 'Hip-hop',
        'rap': 'Hip-hop',
        'trap': 'Hip-hop',
        
        # Jazz and related genres
        'jazz': 'Jazz',
        'bebop': 'Jazz',
        'fusion': 'Jazz',
        'smooth jazz': 'Jazz',
        
        # Country and related genres
        'country': 'Country',
        'bluegrass': 'Country',
        'americana': 'Country',
        'country rock': 'Country',
        
        # Classical and related genres
        'classical': 'Classical',
        'baroque': 'Classical',
        'opera': 'Classical',
        'orchestral': 'Classical',
        'symphony': 'Classical',
        
        # Folk and related genres
        'folk': 'Folk',
        'acoustic': 'Folk',
        'singer-songwriter': 'Folk',
        'traditional': 'Folk',
        
        # Latin and related genres
        'latin': 'Latin',
        'salsa': 'Latin',
        'bossa nova': 'Latin',
        'reggaeton': 'Latin',
        'samba': 'Latin',
        
        # Reggae and related genres
        'reggae': 'Reggae',
        'dub': 'Reggae',
        'ska': 'Reggae',
        'dancehall': 'Reggae',
        
        # Soundtrack and related genres
        'soundtrack': 'Soundtrack',
        'score': 'Soundtrack',
        'film score': 'Soundtrack',
        'film': 'Soundtrack',
        'movie': 'Soundtrack',
        
        # Funk and related genres
        'funk': 'Funk',
        'soul': 'Funk',
        'r&b': 'Funk',
        'rhythm and blues': 'Funk',
        
        # Gospel and related genres
        'gospel': 'Gospel',
        'christian': 'Gospel',
        'spiritual': 'Gospel',
        'religious': 'Gospel',
        
        # World music
        'world': 'World',
        'african': 'World',
        'asian': 'World',
        'celtic': 'World',
        'middle eastern': 'World',
    }
    
    # The set of valid genres in our system
    VALID_GENRES = {
        'Pop', 'Rock', 'Country', 'Jazz', 'Gospel', 'Funk',
        'Soundtrack', 'Hip-hop', 'Latin', 'Electronic',
        'Reggae', 'Classical', 'Folk', 'World'
    }
    
    def __init__(self, user_agent="BoomboxdApp/1.0 +http://boomboxd.com", token=None):
        self.user_agent = user_agent
        # Use the provided token or get from environment
        self.token = token
        self.consumer_key = os.environ.get('DISCOGS_CONSUMER_KEY')
        self.consumer_secret = os.environ.get('DISCOGS_CONSUMER_SECRET')
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum seconds between requests to respect rate limits
        
    def _make_request(self, endpoint, params=None):
        """Make a rate-limited request to Discogs API"""
        # Rate limiting - ensure minimum time between requests
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        
        if params is None:
            params = {}
            
        # Add authentication token if available
        headers = {
            'User-Agent': self.user_agent
        }
        
        # Add auth header for token authentication
        if self.token:
            headers['Authorization'] = f'Discogs token={self.token}'
        elif self.consumer_key and self.consumer_secret:
            params['key'] = self.consumer_key
            params['secret'] = self.consumer_secret
        
        url = f"{self.BASE_URL}/{endpoint}"
        logger.info(f"Making Discogs API request to: {url} with params: {params}")
        
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
    
    def search_album(self, title: str, artist: Optional[str] = None) -> List[Dict]:
        """
        Search for albums (releases) in the Discogs database
        """
        params = {
            'type': 'master',  # Use 'master' to get canonical releases instead of all versions
            'title': title,
            'format': 'album',
            'per_page': 10  # Limit to 10 results to avoid excessive API calls
        }
        
        if artist:
            params['artist'] = artist
        
        data = self._make_request("database/search", params)
        if not data:
            logger.warning(f"No Discogs data found for album: {title}")
            return []
            
        results = []
        
        for item in data.get('results', []):
            # Log the raw data for debugging
            logger.info(f"Raw Discogs result: {item}")
            
            # Extract artist from the title if it contains " - "
            item_artist = item.get('artist', '')
            if not item_artist and ' - ' in item.get('title', ''):
                parts = item.get('title', '').split(' - ', 1)
                item_artist = parts[0].strip()
                item_title = parts[1].strip() if len(parts) > 1 else item.get('title', '')
            else:
                item_title = item.get('title', '')
            
            # Extract and format year
            year = item.get('year', '')
            release_date = f"{year}-01-01" if year and year.isdigit() else ''
            
            # Only get items with a valid title and artist
            if not item_title or not item_artist:
                continue
                
            result = {
                'id': str(item.get('id', '')),
                'title': item_title,
                'artist': item_artist,
                'release_date': release_date,
                'cover_art_url': item.get('cover_image'),
                'thumb_url': item.get('thumb'),
                'country': item.get('country', ''),
                'genres': item.get('genre', []),
                'styles': item.get('style', []),
                'discogs_url': item.get('uri', ''),
                'master_id': item.get('master_id', ''),
                'master_url': item.get('master_url', ''),
            }
            
            # Skip fetching additional details to reduce API calls
            results.append(result)
        
        return results
    
    def _get_master_details(self, master_id):
        """Get detailed information about a master release"""
        data = self._make_request(f"masters/{master_id}")
        if not data:
            return None
            
        # Extract most important details
        details = {
            'title': data.get('title', ''),
            'tracks_count': len(data.get('tracklist', [])),
            'genres': data.get('genres', []),
            'styles': data.get('styles', []),
            'year': data.get('year', ''),
        }
        
        # Format release date if year is available
        if details['year'] and str(details['year']).isdigit():
            details['release_date'] = f"{details['year']}-01-01"
            
        # Get the main release data if available
        main_release_id = data.get('main_release')
        if main_release_id:
            main_release = self._make_request(f"releases/{main_release_id}")
            if main_release:
                details['cover_art_url'] = main_release.get('images', [{}])[0].get('uri', '') if main_release.get('images') else ''
                
                # Get a more accurate release date if available
                if main_release.get('released'):
                    try:
                        # Try to parse various date formats
                        date_str = main_release.get('released')
                        # Handle YYYY-MM-DD
                        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                            details['release_date'] = date_str
                        # Handle YYYY-MM
                        elif re.match(r'^\d{4}-\d{2}$', date_str):
                            details['release_date'] = f"{date_str}-01"
                        # Handle YYYY
                        elif re.match(r'^\d{4}$', date_str):
                            details['release_date'] = f"{date_str}-01-01"
                    except Exception as e:
                        logger.warning(f"Error parsing release date: {e}")
                        
        return details 

    def map_genres(self, discogs_genres, discogs_styles):
        """
        Maps Discogs genres and styles to our system's supported genres
        
        Args:
            discogs_genres: List of genre strings from Discogs
            discogs_styles: List of style strings from Discogs
            
        Returns:
            List of mapped genre strings that match our system's supported genres
        """
        mapped_genres = set()
        
        # Process all genres and styles from Discogs
        all_tags = []
        if discogs_genres:
            all_tags.extend(discogs_genres)
        if discogs_styles:
            all_tags.extend(discogs_styles)
        
        # Convert all tags to lowercase for case-insensitive matching
        all_tags = [tag.lower() for tag in all_tags]
        
        # Map each tag to our supported genres
        for tag in all_tags:
            if tag in self.GENRE_MAPPING:
                mapped_genres.add(self.GENRE_MAPPING[tag])
        
        # If we couldn't map any genres, default to "Rock" as a fallback
        if not mapped_genres:
            mapped_genres.add('Rock')
        
        # Make sure all genres are in our valid genres list
        result = list(mapped_genres.intersection(self.VALID_GENRES))
        
        logger.info(f"Mapped Discogs genres {discogs_genres} and styles {discogs_styles} to {result}")
        
        return result 
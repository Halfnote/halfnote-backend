import os
import sys
import requests
import json
import time
from typing import List, Dict, Optional

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Get credentials from environment variables
DISCOGS_CONSUMER_KEY = os.environ.get('DISCOGS_CONSUMER_KEY')
DISCOGS_CONSUMER_SECRET = os.environ.get('DISCOGS_CONSUMER_SECRET')

class DiscogsClient:
    BASE_URL = "https://api.discogs.com"
    
    def __init__(self, user_agent="BoomboxdTestApp/1.0"):
        self.user_agent = user_agent
        self.consumer_key = DISCOGS_CONSUMER_KEY
        self.consumer_secret = DISCOGS_CONSUMER_SECRET
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum seconds between requests
        
    def _make_request(self, endpoint, params=None):
        """Make a rate-limited request to Discogs API"""
        # Rate limiting
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        
        if params is None:
            params = {}
            
        # Add auth headers
        headers = {
            'User-Agent': self.user_agent
        }
        
        # Add credentials to params
        if self.consumer_key and self.consumer_secret:
            params['key'] = self.consumer_key
            params['secret'] = self.consumer_secret
        
        url = f"{self.BASE_URL}/{endpoint}"
        print(f"Making Discogs API request to: {url}")
        print(f"With params: {params}")
        
        response = requests.get(url, params=params, headers=headers)
        self.last_request_time = time.time()
        
        if response.status_code != 200:
            print(f"Discogs API error: {response.status_code} - {response.text}")
            return None
            
        return response.json()
    
    def search_album(self, title: str, artist: Optional[str] = None) -> List[Dict]:
        """Search for albums in the Discogs database"""
        params = {
            'type': 'master',
            'title': title,
            'format': 'album',
        }
        
        if artist:
            params['artist'] = artist
        
        data = self._make_request("database/search", params)
        if not data:
            print(f"No Discogs data found for album: {title}")
            return []
            
        results = []
        
        for item in data.get('results', []):
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
            
            results.append(result)
        
        return results

def main():
    # Display environment variables for debugging
    print(f"DISCOGS_CONSUMER_KEY: {'*' * (len(DISCOGS_CONSUMER_KEY)-4) + DISCOGS_CONSUMER_KEY[-4:] if DISCOGS_CONSUMER_KEY else 'Not set'}")
    print(f"DISCOGS_CONSUMER_SECRET: {'*' * (len(DISCOGS_CONSUMER_SECRET)-4) + DISCOGS_CONSUMER_SECRET[-4:] if DISCOGS_CONSUMER_SECRET else 'Not set'}")
    
    # Create client and search
    client = DiscogsClient()
    query = "Dark Side of the Moon" if len(sys.argv) < 2 else sys.argv[1]
    print(f"Searching for: {query}")
    
    results = client.search_album(query)
    
    print(f"Found {len(results)} results:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main() 
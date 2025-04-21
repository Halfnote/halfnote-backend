import logging
from django.core.cache import cache
from django.conf import settings
import discogs_client

logger = logging.getLogger(__name__)

class ExternalMusicService:
    def __init__(self):
        self.discogs = discogs_client.Client(
            'BoomboxdApp/1.0',
            user_token=settings.DISCOGS_USER_TOKEN
        )
    
    def search_discogs(self, query, cache_key):
        """Search for albums on Discogs with caching"""
        cached_results = cache.get(cache_key)
        if cached_results:
            return cached_results

        try:
            results = self.discogs.search(query, type='release')
            formatted_results = []
            
            for result in results[:10]:  # Limit to first 10 results
                try:
                    release = result.release
                    formatted_results.append({
                        'title': release.title,
                        'artist': release.artists[0].name if release.artists else 'Unknown Artist',
                        'year': release.year,
                        'genres': release.genres or [],
                        'styles': release.styles or [],
                        'cover_image': release.thumb or None,
                        'discogs_id': release.id,
                    })
                except Exception as e:
                    logger.warning(f"Error processing Discogs result: {str(e)}")
                    continue
            
            cache.set(cache_key, formatted_results, timeout=3600)  # Cache for 1 hour
            return formatted_results
            
        except Exception as e:
            logger.error(f"Discogs API error: {str(e)}")
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
import musicbrainzngs
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class MusicBrainzClient:
    def __init__(self):
        musicbrainzngs.set_useragent(
            "Boomboxd",
            "1.0",
            "https://boomboxd.com"
        )

    def search_album(self, title: str, artist: Optional[str] = None) -> List[Dict]:
        try:
            query = f"release:{title}"
            if artist:
                query += f" AND artist:{artist}"
            
            result = musicbrainzngs.search_releases(query=query, limit=5)
            releases = result.get('release-list', [])
            
            formatted_releases = []
            for release in releases:
                formatted_release = {
                    'id': release['id'],
                    'title': release.get('title', ''),
                    'artist': release.get('artist-credit-phrase', ''),
                    'release_date': release.get('date', ''),
                }
                
                # Get cover art if available
                try:
                    cover_art = musicbrainzngs.get_image_list(release['id'])
                    if cover_art and cover_art['images']:
                        formatted_release['cover_art_url'] = cover_art['images'][0]['thumbnails']['large']
                except:
                    formatted_release['cover_art_url'] = None
                
                formatted_releases.append(formatted_release)
            
            return formatted_releases
        except Exception as e:
            logger.error(f"MusicBrainz search error: {str(e)}")
            return []

    def get_album_details(self, mbid: str) -> Optional[Dict]:
        try:
            result = musicbrainzngs.get_release_by_id(
                mbid,
                includes=['artists', 'recordings', 'genres']
            )
            release = result['release']
            
            return {
                'id': release['id'],
                'title': release.get('title', ''),
                'artist': release.get('artist-credit-phrase', ''),
                'release_date': release.get('date', ''),
                'genres': [tag['name'] for tag in release.get('tag-list', [])],
            }
        except Exception as e:
            logger.error(f"MusicBrainz get_album_details error: {str(e)}")
            return None

    def search_single(self, title: str, artist: Optional[str] = None) -> List[Dict]:
        try:
            query = f"recording:{title}"
            if artist:
                query += f" AND artist:{artist}"
            
            result = musicbrainzngs.search_recordings(query=query, limit=5)
            recordings = result.get('recording-list', [])
            
            formatted_recordings = []
            for recording in recordings:
                formatted_recording = {
                    'id': recording['id'],
                    'title': recording.get('title', ''),
                    'artist': recording.get('artist-credit-phrase', ''),
                    'release_date': recording.get('first-release-date', ''),
                }
                formatted_recordings.append(formatted_recording)
            
            return formatted_recordings
        except Exception as e:
            logger.error(f"MusicBrainz search_single error: {str(e)}")
            return [] 
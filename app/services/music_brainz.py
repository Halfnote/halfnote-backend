import musicbrainzngs
from ..models import Album, Single
from app import db
import uuid

# Set up MusicBrainz client
musicbrainzngs.set_useragent("Boomboxd", "1.0")

def fetch_album_from_musicbrainz(album_title, artist_name):
    try:
        result = musicbrainzngs.search_releases(album=album_title, artist=artist_name, limit=1)
        if result['release-list']:
            release = result['release-list'][0]
            album_id = release['id']
            title = release['title']
            artist = artist_name
            artwork_url = None  # MusicBrainz doesn't provide artwork directly
            release_date = release.get('date')
            tracklist = fetch_tracklist_from_musicbrainz(album_id)
            genres = fetch_genres_from_musicbrainz(album_id)

            # Store the album in the database
            new_album = Album(
                album_id=album_id,
                title=title,
                artist=artist,
                artwork_url=artwork_url,
                release_date=release_date,
                tracklist=tracklist,
                genres=genres,
                api_source='MusicBrainz'
            )
            db.session.add(new_album)
            db.session.commit()

            return new_album
        else:
            return None
    except Exception as e:
        print(f"Error fetching album from MusicBrainz: {e}")
        return None

def fetch_tracklist_from_musicbrainz(album_id):
    try:
        result = musicbrainzngs.get_release_by_id(album_id, includes=['recordings'])
        tracks = result['release']['medium-list'][0]['track-list']
        tracklist = [{"title": track['recording']['title']} for track in tracks]
        return tracklist
    except Exception as e:
        print(f"Error fetching tracklist from MusicBrainz: {e}")
        return []

def fetch_genres_from_musicbrainz(album_id):
    try:
        result = musicbrainzngs.get_release_by_id(album_id, includes=['tags'])
        tags = result['release'].get('tag-list', [])
        genres = [tag['name'] for tag in tags]
        return genres
    except Exception as e:
        print(f"Error fetching genres from MusicBrainz: {e}")
        return []

def fetch_single_from_musicbrainz(single_title, artist_name):
    try:
        result = musicbrainzngs.search_recordings(recording=single_title, artist=artist_name, limit=1)
        if result['recording-list']:
            recording = result['recording-list'][0]
            single_id = recording['id']
            title = recording['title']
            artist = artist_name
            artwork_url = None  # MusicBrainz doesn't provide artwork directly
            release_date = recording.get('first-release-date')
            track = {"title": title}

            # Store the single in the database
            new_single = Single(
                single_id=single_id,
                title=title,
                artist=artist,
                artwork_url=artwork_url,
                release_date=release_date,
                track=track,
                api_source='MusicBrainz'
            )
            db.session.add(new_single)
            db.session.commit()

            return new_single
        else:
            return None
    except Exception as e:
        print(f"Error fetching single from MusicBrainz: {e}")
        return None

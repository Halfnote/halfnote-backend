from flask import Blueprint, request, jsonify
from models import Album, Review
from app import db
from app.services.music_brainz import fetch_album_from_musicbrainz

bp = Blueprint('albums', __name__, url_prefix='/albums')

@bp.route('/<album_id>', methods=['GET'])
def get_album(album_id):
    album = Album.query.get(album_id)
    if not album:
        # Fetch album from MusicBrainz if not found locally
        album_title = request.args.get('title')
        artist_name = request.args.get('artist')
        if album_title and artist_name:
            album = fetch_album_from_musicbrainz(album_title, artist_name)
            if not album:
                return jsonify({"error": "Album not found"}), 404
        else:
            return jsonify({"error": "Album not found"}), 404

    return jsonify({
        "album_id": album.album_id,
        "title": album.title,
        "artist": album.artist,
        "artwork_url": album.artwork_url,
        "release_date": album.release_date,
        "tracklist": album.tracklist
    }), 200


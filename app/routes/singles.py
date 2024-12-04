from flask import Blueprint, request, jsonify
from models import Single, Review
from app import db
from app.services.music_brainz import fetch_single_from_musicbrainz

bp = Blueprint('singles', __name__, url_prefix='/singles')

@bp.route('/<single_id>', methods=['GET'])
def get_single(single_id):
    single = Single.query.get(single_id)
    if not single:
        # Fetch single from MusicBrainz if not found locally
        single_title = request.args.get('title')
        artist_name = request.args.get('artist')
        if single_title and artist_name:
            single = fetch_single_from_musicbrainz(single_title, artist_name)
            if not single:
                return jsonify({"error": "Single not found"}), 404
    else:
            return jsonify({"error": "Single not found"}), 404

    return jsonify({
        "single_id": single.single_id,
        "title": single.title,
        "artist": single.artist,
        "artwork_url": single.artwork_url,
        "release_date": single.release_date,
        "track": single.track
    }), 200



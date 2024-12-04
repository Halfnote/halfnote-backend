from flask import Blueprint, request, jsonify
from models import Review, Album, Single
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid

bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@bp.route('/', methods=['POST'])
@jwt_required()
def submit_review():
    user_id = get_jwt_identity()
    data = request.get_json()
    album_id = data.get('album_id')
    single_id = data.get('single_id')
    rating = data.get('rating')
    review_text = data.get('review_text')

    if not rating or (not album_id and not single_id):
        return jsonify({"error": "Rating and either album_id or single_id are required"}), 400

    # Check if the album or single exists
    if album_id:
        if not Album.query.get(album_id):
            return jsonify({"error": "Album not found"}), 404
    if single_id:
        if not Single.query.get(single_id):
            return jsonify({"error": "Single not found"}), 404

    new_review = Review(
        review_id=str(uuid.uuid4()),
        user_id=user_id,
        album_id=album_id,
        single_id=single_id,
        rating=rating,
        review_text=review_text
    )
    db.session.add(new_review)
    db.session.commit()

    return jsonify({"message": "Review submitted successfully"}), 201

@bp.route('/user/<user_id>', methods=['GET'])
@jwt_required()
def get_user_reviews(user_id):
    reviews = Review.query.filter_by(user_id=user_id).all()
    if not reviews:
        return jsonify({"error": "No reviews found for this user"}), 404

    reviews_list = [{
        "review_id": review.review_id,
        "album_id": review.album_id,
        "single_id": review.single_id,
        "rating": review.rating,
        "review_text": review.review_text,
        "timestamp": review.timestamp
    } for review in reviews]

    return jsonify(reviews_list), 200

@bp.route('/album/<album_id>', methods=['GET'])
def get_album_reviews(album_id):
    # Check if the album exists in the database
    album = Album.query.get(album_id)
    if not album:
        return jsonify({"error": "Album not found"}), 404

    # Fetch all reviews associated with this album
    reviews = Review.query.filter_by(album_id=album_id).all()
    if not reviews:
        return jsonify({"message": "No reviews found for this album"}), 200

    # Format the reviews for the response
    reviews_list = [{
        "review_id": review.review_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "review_text": review.review_text,
        "timestamp": review.timestamp
    } for review in reviews]

    return jsonify(reviews_list), 200

@bp.route('/single/<single_id>', methods=['GET'])
def get_single_reviews(single_id):
    # Check if the single exists in the database
    single = Single.query.get(single_id)
    if not single:
        return jsonify({"error": "Single not found"}), 404

    # Fetch all reviews associated with this single
    reviews = Review.query.filter_by(single_id=single_id).all()
    if not reviews:
        return jsonify({"message": "No reviews found for this single"}), 200

    # Format the reviews for the response
    reviews_list = [{
        "review_id": review.review_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "review_text": review.review_text,
        "timestamp": review.timestamp
    } for review in reviews]

    return jsonify(reviews_list), 200
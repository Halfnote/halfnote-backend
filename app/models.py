from datetime import datetime, timezone
from app import db

# TODO: Add pinned reviews (max: 6)
# TODO: Add pinned albums (max: 4)
class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    reviews = db.relationship('Review', backref='user', lazy=True)

# TODO: Add genres to the data model
class Album(db.Model):
    __tablename__ = 'Albums'
    album_id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    artist = db.Column(db.String(120), nullable=False)
    artwork_url = db.Column(db.String(255))
    release_date = db.Column(db.Date)
    tracklist = db.Column(db.JSON)
    genres = db.Column(db.JSON, default=[])
    api_source = db.Column(db.String(20))

    reviews = db.relationship('Review', backref='album', lazy=True)
    pinned_reviews = db.Column(db.JSON, default=[])
    pinned_albums = db.Column(db.JSON, default=[])

class Single(db.Model):
    __tablename__ = 'Singles'
    single_id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    artist = db.Column(db.String(120), nullable=False)
    artwork_url = db.Column(db.String(255))
    release_date = db.Column(db.Date)
    track = db.Column(db.JSON)
    genres = db.Column(db.JSON, default=[])
    api_source = db.Column(db.String(20))

    reviews = db.relationship('Review', backref='single', lazy=True)


# TODO: Add number of likes per each review row
class Review(db.Model):
    __tablename__ = 'Reviews'
    review_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.user_id'), nullable=False)
    album_id = db.Column(db.String, db.ForeignKey('albums.album_id'), nullable=True)
    single_id = db.Column(db.String, db.ForeignKey('singles.single_id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    likes = db.Column(db.Integer, default=0)


#!/usr/bin/env python
"""
Utility script for managing music data in Boomboxd

This script allows you to:
1. Search for albums
2. Add albums to your library
3. Add artists
4. Add reviews

Usage:
    python manage_music.py search "Pink Floyd"
    python manage_music.py add_album 10362 "The Dark Side of the Moon" "Pink Floyd" "1973-03-01"
    python manage_music.py add_artist "Radiohead"
    python manage_music.py add_review <album_id> 9.5 "One of the best albums ever made"
"""

import os
import sys
import uuid
import django
import json
import requests
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boomboxd.settings')
django.setup()

from django.contrib.auth import get_user_model
from music.models import Album, Artist, Genre
from reviews.models import Review
from music.services.discogs import DiscogsClient

User = get_user_model()

def search_album(query):
    """Search for an album using Discogs API"""
    print(f"Searching for: {query}")
    
    discogs_client = DiscogsClient()
    results = discogs_client.search_album(query)
    
    if not results:
        print("No results found")
        return
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results[:10], 1):  # Show first 10 results
        artist = result.get('artist', 'Unknown')
        title = result.get('title', 'Unknown')
        release_date = result.get('release_date', 'Unknown date')
        discogs_id = result.get('id', '')
        genres = ", ".join(result.get('genres', []))
        
        print(f"{i}. [{discogs_id}] {title} by {artist} ({release_date}) - {genres}")
    
    return results

def add_album(discogs_id, title, artist_name, release_date=None, cover_art_url=None):
    """Add an album to the database"""
    print(f"Adding album: {title} by {artist_name}")
    
    # Get or create the artist
    artist, created = Artist.objects.get_or_create(name=artist_name)
    if created:
        print(f"Created new artist: {artist.name}")
    else:
        print(f"Using existing artist: {artist.name}")
    
    # Check if album already exists
    if Album.objects.filter(discogs_id=discogs_id).exists():
        album = Album.objects.get(discogs_id=discogs_id)
        print(f"Album already exists: {album.title} by {album.artist.name}")
        return album
    
    # Handle release date
    if not release_date:
        release_date = "1970-01-01"
    
    # Create the album
    album = Album.objects.create(
        id=uuid.uuid4(),
        title=title,
        artist=artist,
        release_date=release_date,
        cover_art_url=cover_art_url,
        discogs_id=discogs_id
    )
    
    print(f"Successfully added album: {album.title} by {album.artist.name}")
    print(f"Album ID: {album.id}")
    
    return album

def add_artist(name):
    """Add an artist to the database"""
    artist, created = Artist.objects.get_or_create(name=name)
    if created:
        print(f"Created new artist: {artist.name}")
    else:
        print(f"Artist already exists: {artist.name}")
    
    return artist

def add_review(album_id, rating, text=""):
    """Add a review for an album"""
    try:
        album = Album.objects.get(id=album_id)
    except Album.DoesNotExist:
        print(f"Album with ID {album_id} not found")
        return None
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username="testuser",
        defaults={"password": "pbkdf2_sha256$600000$testpassword123secure"}
    )
    
    # Validate rating
    try:
        rating = float(rating)
        if not (1 <= rating <= 10):
            print("Rating must be between 1 and 10")
            return None
    except ValueError:
        print("Rating must be a number between 1 and 10")
        return None
    
    # Create the review (without specifying an ID)
    review = Review.objects.create(
        user=user,
        album=album,
        rating=rating,
        text=text
    )
    
    # Update album average rating and total ratings
    album.total_ratings += 1
    if album.total_ratings == 1:
        album.average_rating = rating
    else:
        album.average_rating = ((album.average_rating * (album.total_ratings - 1)) + rating) / album.total_ratings
    album.save()
    
    print(f"Added review for {album.title} by {album.artist.name}")
    print(f"Rating: {rating}/10")
    print(f"Review ID: {review.id}")
    
    return review

def print_usage():
    print("Usage:")
    print("  python manage_music.py search <query>")
    print("  python manage_music.py add_album <discogs_id> <title> <artist> [<release_date>] [<cover_url>]")
    print("  python manage_music.py add_artist <name>")
    print("  python manage_music.py add_review <album_id> <rating> [<text>]")
    print("  python manage_music.py list_albums")
    print("  python manage_music.py list_artists")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "search" and len(sys.argv) >= 3:
        search_album(sys.argv[2])
    
    elif command == "add_album" and len(sys.argv) >= 5:
        discogs_id = sys.argv[2]
        title = sys.argv[3]
        artist = sys.argv[4]
        release_date = sys.argv[5] if len(sys.argv) >= 6 else None
        cover_url = sys.argv[6] if len(sys.argv) >= 7 else None
        add_album(discogs_id, title, artist, release_date, cover_url)
    
    elif command == "add_artist" and len(sys.argv) >= 3:
        add_artist(sys.argv[2])
    
    elif command == "add_review" and len(sys.argv) >= 4:
        album_id = sys.argv[2]
        rating = sys.argv[3]
        text = " ".join(sys.argv[4:]) if len(sys.argv) >= 5 else ""
        add_review(album_id, rating, text)
    
    elif command == "list_albums":
        albums = Album.objects.all().order_by("-created_at")
        print(f"Found {albums.count()} albums:")
        for album in albums:
            print(f"[{album.id}] {album.title} by {album.artist.name} ({album.release_date}) - Rating: {album.average_rating}/10 ({album.total_ratings} reviews)")
    
    elif command == "list_artists":
        artists = Artist.objects.all().order_by("name")
        print(f"Found {artists.count()} artists:")
        for artist in artists:
            print(f"[{artist.id}] {artist.name}")
    
    else:
        print_usage()
        sys.exit(1) 
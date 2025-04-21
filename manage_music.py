#!/usr/bin/env python
"""
Boomboxd Command Line Utility
=============================

This is a simple command-line tool for managing music data in the Boomboxd backend.
It helps you search, add, and manage albums and reviews without using the web API.

Examples:
---------
  # Search for an album
  python manage_music.py search "Pink Floyd"

  # Add an album to your library
  python manage_music.py add_album 10362 "The Dark Side of the Moon" "Pink Floyd" "1973-03-01"

  # Create a review
  python manage_music.py add_review <album_id> 9.5 "One of the best albums ever made"

  # List all albums in the database
  python manage_music.py list_albums
"""

import os
import sys
import uuid
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boomboxd.settings')
django.setup()

from django.contrib.auth import get_user_model
from music.models import Album, Artist, Genre
from reviews.models import Review
from music.services import ExternalMusicService

User = get_user_model()

#
# Core Functions
#

def search_album(query):
    """
    Search for an album using Discogs API
    
    Args:
        query (str): The search query (artist name, album title, etc.)
    
    Returns:
        list: Search results from Discogs
    """
    print(f"Searching for: {query}")
    
    service = ExternalMusicService()
    cache_key = f'cli_search:{query}'
    results = service.search_discogs(query, cache_key)
    
    if not results:
        print("No results found")
        return
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results[:10], 1):  # Show first 10 results
        artist = result.get('artist', 'Unknown')
        title = result.get('title', 'Unknown')
        year = result.get('year', 'Unknown date')
        discogs_id = result.get('discogs_id', '')
        genres = ", ".join(result.get('genres', []))
        
        print(f"{i}. [{discogs_id}] {title} by {artist} ({year}) - {genres}")
    
    return results

def add_album(discogs_id, title, artist_name, release_date=None, cover_art_url=None):
    """
    Add an album to the database
    
    Args:
        discogs_id (str): The Discogs ID of the album
        title (str): Album title
        artist_name (str): Artist name
        release_date (str, optional): Release date in YYYY-MM-DD format
        cover_art_url (str, optional): URL to album cover artwork
    
    Returns:
        Album: The created or existing album object
    """
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

def add_review(album_id, rating, text=""):
    """
    Add a review for an album
    
    Args:
        album_id (str): The UUID of the album to review
        rating (float): Rating value between 1 and 10
        text (str, optional): Review text
    
    Returns:
        Review: The created review object
    """
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
    
    # Create the review
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

#
# Helper Functions
#

def print_usage():
    """Print command-line usage instructions"""
    print("Boomboxd Command Line Utility")
    print("=============================")
    print("Usage:")
    print("  python manage_music.py search <query>")
    print("  python manage_music.py add_album <discogs_id> <title> <artist> [<release_date>] [<cover_url>]")
    print("  python manage_music.py add_artist <n>")
    print("  python manage_music.py add_review <album_id> <rating> [<text>]")
    print("  python manage_music.py list_albums")
    print("  python manage_music.py list_artists")

#
# Command Line Interface
#

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "search":
        if len(sys.argv) < 3:
            print("Please provide a search query")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        search_album(query)
        
    elif command == "add_album":
        if len(sys.argv) < 5:
            print("Please provide discogs_id, title, and artist")
            sys.exit(1)
        discogs_id = sys.argv[2]
        title = sys.argv[3]
        artist = sys.argv[4]
        release_date = sys.argv[5] if len(sys.argv) > 5 else None
        cover_url = sys.argv[6] if len(sys.argv) > 6 else None
        add_album(discogs_id, title, artist, release_date, cover_url)
        
    elif command == "add_review":
        if len(sys.argv) < 4:
            print("Please provide album_id and rating")
            sys.exit(1)
        album_id = sys.argv[2]
        rating = sys.argv[3]
        text = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        add_review(album_id, rating, text)
        
    elif command == "list_albums":
        albums = Album.objects.all().order_by('-created_at')
        print(f"\nFound {albums.count()} albums:")
        for album in albums:
            print(f"[{album.id}] {album.title} by {album.artist.name}")
            
    elif command == "list_artists":
        artists = Artist.objects.all().order_by('name')
        print(f"\nFound {artists.count()} artists:")
        for artist in artists:
            print(f"[{artist.id}] {artist.name}")
            
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1) 
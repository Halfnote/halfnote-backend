# Boomboxd Backend

A Django-based backend service for the Boomboxd music rating platform. This service integrates with Discogs to provide music metadata and allows users to rate and review albums.

## Core Architecture

```
boomboxd-backend/
├── accounts/            # User authentication and profile management
├── music/               # Album and artist data management
│   ├── services/        # External API integrations (Discogs, Spotify)
│   ├── models.py        # Database models for music data
│   ├── views.py         # API endpoints for music data
│   └── serializers.py   # JSON serialization for API responses
├── reviews/             # User reviews functionality
├── boomboxd/            # Main project configuration
└── manage_music.py      # CLI utility for managing music data
```

## Key Concepts

1. **Albums**: Music releases fetched from Discogs and stored locally
2. **Reviews**: User ratings (1-10 scale) and text reviews for albums, with associated genres
3. **Genres**: Each review can be tagged with one or more genres from a predefined list: Pop, Rock, Country, Jazz, Gospel, Funk, Soundtrack, Hip-hop, Latin, Electronic, Reggae, Classical, Folk, and World

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis

### Installation

1. Create and activate virtual environment:
```shell
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```shell
pip install -r requirements.txt
```

3. Configure environment:
```shell
cp .env.template .env
# Edit .env with your configuration
```

4. Set up database:
```shell
createdb boomboxd
python manage.py migrate
```

5. Create superuser:
```shell
python manage.py createsuperuser
```

6. Run server:
```shell
python manage.py runserver
```

## Usage

### Command Line Utility

```shell
# Search for albums
python manage_music.py search "Pink Floyd"

# Add an album to the database
python manage_music.py add_album <discogs_id> "<title>" "<artist>" "<release_date>" "<cover_url>"

# List all albums
python manage_music.py list_albums
```

### API Endpoints

#### Authentication
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login and get auth token
- `POST /api/auth/logout/` - Logout and clear auth token

#### Albums
- `GET /api/albums/` - List all albums
- `GET /api/albums/{id}/` - Get album details
- `GET /api/albums/search/?q=query` - Search for albums from Discogs
- `POST /api/albums/import_from_discogs/` - Import a Discogs album to library

#### Reviews
- `GET /api/reviews/` - List all reviews
- `POST /api/reviews/` - Create a new review with genres
- `GET /api/reviews/{id}/` - Get review details
- `PUT/DELETE /api/reviews/{id}/` - Update/delete a review

## Genre System

The genre system is designed to be simple and user-driven:

1. Each review can be tagged with one or more genres from a predefined list
2. Genres are stored directly with the review, eliminating complex relationships
3. The same album can be tagged with different genres by different users
4. Genre data can be used for:
   - Finding albums by genre through review aggregation
   - Understanding how different users categorize the same album
   - Discovering music through genre-based exploration

Example review creation with genres:
```json
POST /api/reviews/
{
    "album_id": "uuid",
    "rating": 8,
    "text": "Great album!",
    "genres": ["Rock", "Electronic"]
}
```

## Authentication System

Authentication is handled with JWT tokens stored in HTTP-only cookies for security.

## Features

- 🎵 Music search and metadata from Discogs API
- 🎧 Spotify streaming links and embeds
- 🖼️ Album cover art
- ⭐ User ratings and reviews with genre tagging
- 🔒 Secure authentication with JWT tokens
- 💾 Redis caching for performance

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis
- Spotify Developer Account
- Discogs Developer Account

### Local Development Setup

1. Clone the repository:
```shell
git clone https://github.com/your-username/boomboxd-backend.git
cd boomboxd-backend
```

2. Create and activate virtual environment:
```shell
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```shell
pip install -r requirements.txt
```

4. Create `.env` file from template:
```shell
cp .env.template .env
# Edit .env with your configuration
```

5. Set up the database:
```shell
# If using installed PostgreSQL
createdb boomboxd

# Or start PostgreSQL using Docker
docker run --name boomboxd-postgres \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_USER=boomboxd \
  -e POSTGRES_DB=boomboxd \
  -p 5432:5432 \
  -d postgres

# Start Redis (if using Docker)
docker run --name boomboxd-redis -p 6379:6379 -d redis
# Or if installed locally
brew services start redis  # On macOS

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

6. Run the development server:
```shell
python manage.py runserver
```

## Using the Utility Script

A utility script `manage_music.py` is provided to help manage music data:

```shell
# Search for albums
python manage_music.py search "Pink Floyd"

# Add an album to the database
python manage_music.py add_album <discogs_id> "<title>" "<artist>" "<release_date>" "<cover_url>"

# Add an artist
python manage_music.py add_artist "Pink Floyd"

# Add a review (after adding the album)
python manage_music.py add_review <album_id> 9.5 "One of the best albums ever made"

# List all albums in the database
python manage_music.py list_albums

# List all artists in the database
python manage_music.py list_artists
```

## Workflow

The typical workflow for adding reviews is:

1. **Search** for an album (`/api/albums/search/?q=query`)
2. **Save** the album to the database (either via `save_to_library` API or `manage_music.py add_album`)
3. **Review** the album (requires the album to be in the database first)

## API Documentation

All endpoints return JSON responses. Authentication is handled via JWT tokens stored in HTTP-only cookies.

### Base URL

For local development: `http://localhost:8000/api/`
For production: `https://api.boomboxd.com/api/`

### Authentication Endpoints

#### Register New User
```json
POST /api/auth/register/
Content-Type: application/json

{
    "username": "string",
    "email": "string",
    "password": "string"
}

Response (200):
{
    "id": "integer",
    "username": "string",
    "email": "string"
}
```

#### Login
```json
POST /api/auth/login/
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}

Response (200):
{
    "message": "Login successful"
}
```
Note: Sets HTTP-only auth cookies

#### Refresh Token
```json
POST /api/auth/refresh/

Response (200):
{
    "message": "Token refresh successful"
}
```
Note: Updates HTTP-only auth cookies

#### Logout
```json
POST /api/auth/logout/

Response (200):
{
    "message": "Logout successful"
}
```
Note: Clears auth cookies

#### Get Current User
```json
GET /api/auth/user/

Response (200):
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "date_joined": "datetime"
}
```

### Album Endpoints

#### List Albums
```json
GET /api/albums/
Query Parameters:
- page: integer (optional)
- ordering: string (optional, e.g., "-release_date", "average_rating")
- artist_id: integer (optional)
- genre_id: integer (optional)
- year: integer (optional)

Response (200):
{
    "count": "integer",
    "next": "string (url)",
    "previous": "string (url)",
    "results": [
        {
            "id": "uuid",
            "title": "string",
            "artist": {
                "id": "integer",
                "name": "string"
            },
            "release_date": "YYYY-MM-DD",
            "cover_art_url": "string",
            "spotify_url": "string",
            "spotify_embed_url": "string",
            "genres": [
                {
                    "id": "integer",
                    "name": "string"
                }
            ],
            "average_rating": "float(1.0-10.0)",
            "total_ratings": "integer",
            "created_at": "datetime"
        }
    ]
}
```

#### Get Single Album
```json
GET /api/albums/{id}/

Response (200): 
{
    "id": "uuid",
    "title": "string",
    "artist": {
        "id": "integer",
        "name": "string"
    },
    "release_date": "YYYY-MM-DD",
    "cover_art_url": "string",
    "spotify_url": "string",
    "spotify_embed_url": "string",
    "genres": [
        {
            "id": "integer",
            "name": "string"
        }
    ],
    "average_rating": "float(1.0-10.0)",
    "total_ratings": "integer",
    "reviews": [
        {
            "id": "uuid",
            "user": {
                "id": "integer",
                "username": "string"
            },
            "rating": "integer(1-10)",
            "text": "string",
            "created_at": "datetime"
        }
    ],
    "created_at": "datetime"
}
```

#### Search Albums
```json
GET /api/albums/search/
Query Parameters:
- q: string (required)
- type: string (optional, values: "album", "artist", "all", default: "all")
- limit: integer (optional, default: 20)

Response (200): 
{
    "results": [
        {
            "discogs_id": "string",
            "title": "string",
            "artist": "string",
            "cover_art_url": "string",
            "year": "string",
            "genres": ["string"],
            "styles": ["string"],
            "in_library": boolean
        }
    ],
    "next_page": integer | null
}
```

#### Save Album to Library
```json
POST /api/albums/save_to_library/
Content-Type: application/json
Authorization: Bearer <token>

{
    "discogs_id": "string",
    "title": "string",
    "artist": "string",
    "release_date": "YYYY-MM-DD",
    "cover_art_url": "string",
    "genres": ["string"],
    "styles": ["string"]
}

Response (201):
{
    "detail": "Album saved to library",
    "album": {
        "id": "uuid",
        "title": "string",
        "artist": {
            "id": "integer",
            "name": "string"
        },
        "release_date": "YYYY-MM-DD",
        "cover_art_url": "string",
        "genres": [
            {
                "id": "integer",
                "name": "string"
            }
        ],
        "average_rating": 0,
        "total_ratings": 0
    }
}
```

### Artist Endpoints

#### List Artists
```json
GET /api/artists/
Query Parameters:
- page: integer (optional)
- ordering: string (optional, e.g., "name")
- search: string (optional)

Response (200):
{
    "count": "integer",
    "next": "string (url)",
    "previous": "string (url)",
    "results": [
        {
            "id": "integer",
            "name": "string",
            "albums_count": "integer"
        }
    ]
}
```

#### Get Single Artist
```json
GET /api/artists/{id}/

Response (200):
{
    "id": "integer",
    "name": "string",
    "albums": [
        {
            "id": "uuid",
            "title": "string",
            "release_date": "YYYY-MM-DD",
            "cover_art_url": "string",
            "average_rating": "float(1.0-10.0)"
        }
    ]
}
```

### Review Endpoints

#### List Reviews
```json
GET /api/reviews/
Query Parameters:
- album_id: string (optional)
- user: string (optional)
- page: integer (optional)
- ordering: string (optional, e.g., "-created_at", "-rating")

Response (200):
{
    "count": "integer",
    "next": "string (url)",
    "previous": "string (url)",
    "results": [
        {
            "id": "uuid",
            "user": {
                "id": "integer",
                "username": "string"
            },
            "album": {
                "id": "uuid",
                "title": "string",
                "artist": {
                    "id": "integer",
                    "name": "string"
                },
                "cover_art_url": "string"
            },
            "rating": "integer(1-10)",
            "text": "string",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    ]
}
```

#### Create Review
```json
POST /api/reviews/
Content-Type: application/json

{
    "album_id": "uuid",
    "rating": "integer(1-10)",
    "text": "string",
    "genres": ["string"]  // Array of genre names from predefined list
}

Response (201):
{
    "id": "uuid",
    "user": "string",
    "album": {
        "id": "uuid",
        "title": "string",
        "artist": "string",
        "cover_image_url": "string"
    },
    "rating": "integer(1-10)",
    "text": "string",
    "genres": ["string"],
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### Get Single Review
```json
GET /api/reviews/{id}/

Response (200): 
{
    "id": "uuid",
    "user": {
        "id": "integer",
        "username": "string"
    },
    "album": {
        "id": "uuid",
        "title": "string",
        "artist": {
            "id": "integer",
            "name": "string"
        },
        "cover_art_url": "string"
    },
    "rating": "integer(1-10)",
    "text": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### Update Review
```json
PUT /api/reviews/{id}/
PATCH /api/reviews/{id}/  # For partial updates
Content-Type: application/json

{
    "rating": "integer(1-10)",
    "text": "string",
    "genres": ["string"]  // Optional, array of genre names
}

Response (200): Updated review object
```

#### Delete Review
```json
DELETE /api/reviews/{id}/

Response (204): No content
```

### User Profile Endpoints

#### Get User Profile
```json
GET /api/users/{username}/

Response (200):
{
    "id": "integer",
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "bio": "string",
    "avatar_url": "string",
    "date_joined": "datetime",
    "reviews_count": "integer",
    "followers_count": "integer",
    "following_count": "integer"
}
```

#### Get User Reviews
```json
GET /api/users/{username}/reviews/
Query Parameters:
- page: integer (optional)

Response (200): List of review objects
```

#### Follow User
```json
POST /api/users/{username}/follow/

Response (200):
{
    "detail": "Successfully followed user"
}
```

#### Unfollow User
```json
POST /api/users/{username}/unfollow/

Response (200):
{
    "detail": "Successfully unfollowed user"
}
```

### Genre Endpoints

#### List Genres
```json
GET /api/genres/
Query Parameters:
- ordering: string (optional, e.g., "name", "-albums_count")

Response (200):
[
    {
        "id": "integer",
        "name": "string",
        "albums_count": "integer"
    }
]
```

> **Note:** The system supports these specific genres: Pop, Rock, Country, Jazz, Gospel, Funk, Soundtrack, Hip-hop, Latin, Electronic, Reggae, Classical, Folk, and World.

#### Get Albums by Genre
```json
GET /api/genres/{id}/albums/
Query Parameters:
- page: integer (optional)

Response (200): List of album objects
```

### System Endpoints

#### Health Check
```json
GET /health/

Response (200):
{
    "status": "healthy",
    "database": "healthy",
    "cache": "healthy",
    "version": "string"
}
```

### Error Responses

All endpoints may return these error responses:

```json
401 Unauthorized:
{
    "detail": "Authentication credentials were not provided."
}

403 Forbidden:
{
    "detail": "You do not have permission to perform this action."
}

404 Not Found:
{
    "detail": "Not found."
}

400 Bad Request:
{
    "field_name": [
        "Error message"
    ]
}

500 Internal Server Error:
{
    "detail": "Internal server error"
}
```

## Frontend Integration

### Making Authenticated Requests

Include `credentials: 'include'` in fetch calls to handle cookies:

```javascript
// Example: Search for albums
const searchAlbums = async (query) => {
  const response = await fetch(`/api/albums/search/?q=${query}`, {
    credentials: 'include'
  });
  return response.json();
};

// Example: Submit a review with genres
const submitReview = async (albumId, rating, text, genres) => {
  const response = await fetch('/api/reviews/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      album_id: albumId,
      rating: rating,  // 1-10 rating
      text: text,
      genres: genres  // Array of genre names, e.g. ["Rock", "Electronic"]
    })
  });
  return response.json();
};
```

## Deployment

### Docker Deployment

1. Build and run with Docker Compose:
```shell
docker-compose up --build
```

### AWS Deployment

1. Create AWS resources:
   - RDS PostgreSQL instance
   - ElastiCache Redis instance
   - Elastic Beanstalk environment

2. Configure environment variables in AWS console

3. Deploy:
```shell
eb init
eb create boomboxd-env
eb deploy
```

## Environment Variables

Required environment variables in `.env`:

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True/False
ALLOWED_HOSTS=comma,separated,hosts

DB_NAME=database_name
DB_USER=database_user
DB_PASSWORD=database_password
DB_HOST=database_host
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE) 

## Filtering, Searching and Ordering

The API now supports advanced filtering, searching, and ordering capabilities:

### Album Filtering

```
# Filter by exact match
GET /api/albums/?artist__name=Pink Floyd
GET /api/albums/?genres__name=Rock

# Filter by containment (case-insensitive)
GET /api/albums/?title__icontains=dark

# Filter by range
GET /api/albums/?release_date__year=1973
GET /api/albums/?release_date__year__gte=1970&release_date__year__lte=1979
GET /api/albums/?average_rating__gte=8.5
```

### Review Filtering

```
# Filter by user
GET /api/reviews/?user__username=testuser

# Filter by album
GET /api/reviews/?album__id=123e4567-e89b-12d3-a456-426614174000
GET /api/reviews/?album__title__icontains=dark

# Filter by rating
GET /api/reviews/?rating__gte=8
```

### Searching

```
# Search across multiple fields
GET /api/albums/?search=pink floyd
GET /api/reviews/?search=excellent
```

### Ordering

```
# Order by fields
GET /api/albums/?ordering=release_date  # Ascending
GET /api/albums/?ordering=-average_rating  # Descending

# Order by multiple fields
GET /api/albums/?ordering=-average_rating,title
```

The available filter fields are:
- Albums: title, artist__name, genres__name, release_date, average_rating

## Setup Instructions

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/your-username/boomboxd-backend.git
   cd boomboxd-backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create `.env` file from template:
   ```
   cp .env.template .env
   ```
   Then, edit the `.env` file to add your credentials.

5. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

### Deploying to Vercel

1. Create a new project on Vercel.

2. Add all environment variables from your `.env` file to the Vercel project:
   - Go to Project Settings > Environment Variables
   - Add each key-value pair
   - Make sure to set `VERCEL=1`
   - For the database, use your Supabase connection pooler details

3. Configure your Vercel project:
   - Set the Framework Preset to Other
   - The root directory should be `/`
   - Build command can be empty or `pip install -r requirements.txt`
   - Output directory can be empty

4. Deploy and enjoy!

## Database Setup

For production, we use a Supabase PostgreSQL database. To set it up:

1. Create a database in Supabase.

2. Run migrations to set up the database schema locally:
   ```bash
   # Create a script to use Supabase connection data
   ./migrate_supabase.sh
   ```

3. Add these environment variables to Vercel:
   ```
   DB_NAME=postgres
   DB_USER=postgres.yoursubdomain
   DB_PASSWORD=your-password
   DB_HOST=your-pooler-host.supabase.co
   DB_PORT=6543
   ```

## Security Notes

- Always keep your .env file out of version control.
- Never commit sensitive credentials to the repository.
- For production, use environment variables in Vercel for all sensitive data.
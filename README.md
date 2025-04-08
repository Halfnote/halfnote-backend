# Boomboxd Backend

A Django-based backend service for the Boomboxd music rating platform. This service integrates with MusicBrainz and Spotify to provide music metadata, streaming links, and allows users to rate and review music.

## Features

- 🎵 Music search and metadata from MusicBrainz
- 🎧 Spotify streaming links and embeds
- 🖼️ Album/single cover art
- ⭐ User ratings and reviews
- 🔒 Secure authentication with HTTP-only cookies
- 💾 Redis caching for performance
- 🎸 Genre support

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis
- Spotify Developer Account

### Local Development Setup

1. Clone the repository:
```shell
git clone <repository-url>
cd boomboxd-backend
```

2. Create and activate virtual environment:
```shell
python -m venv venv
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
# Start PostgreSQL (using Docker)
docker run --name boomboxd-postgres \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_USER=boomboxd \
  -e POSTGRES_DB=boomboxd \
  -p 5432:5432 \
  -d postgres

# Start Redis
docker run --name boomboxd-redis -p 6379:6379 -d redis

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

6. Run the development server:
```shell
python manage.py runserver
```

## API Documentation

All endpoints return JSON responses. Authentication is handled via HTTP-only cookies.

### Authentication Endpoints

#### Register New User
```
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
```
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
```
POST /api/auth/refresh/

Response (200):
{
    "message": "Token refresh successful"
}
```
Note: Updates HTTP-only auth cookies

#### Logout
```
POST /api/auth/logout/

Response (200):
{
    "message": "Logout successful"
}
```
Note: Clears auth cookies

### Album Endpoints

#### List Albums
```
GET /api/albums/
Query Parameters:
- page: integer (optional)
- ordering: string (optional, e.g., "-release_date", "average_rating")

Response (200):
{
    "count": "integer",
    "next": "string (url)",
    "previous": "string (url)",
    "results": [
        {
            "id": "uuid",
            "title": "string",
            "artist": "string",
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
```
GET /api/albums/{id}/

Response (200): Single album object
```

#### Search Albums
```
GET /api/albums/search/
Query Parameters:
- q: string (required)

Response (200): Array of album objects
```

### Single Endpoints

#### List Singles
```
GET /api/singles/
Query Parameters:
- page: integer (optional)
- ordering: string (optional)
```

#### Get Single Track
```
GET /api/singles/{id}/

Response (200): Single track object
```

#### Search Singles
```
GET /api/singles/search/
Query Parameters:
- q: string (required)

Response (200): Array of single objects
```

### Review Endpoints

#### List Reviews
```
GET /api/reviews/
Query Parameters:
- album_id: string (optional)
- single_id: string (optional)
- user: string (optional)
- page: integer (optional)

Response (200):
{
    "count": "integer",
    "next": "string (url)",
    "previous": "string (url)",
    "results": [
        {
            "id": "uuid",
            "user": "string",
            "album": {object} | null,
            "single": {object} | null,
            "rating": "integer(1-10)",
            "text": "string",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    ]
}
```

#### Create Review
```
POST /api/reviews/
Content-Type: application/json

{
    "album_id": "uuid",  // Either album_id or single_id required
    "single_id": "uuid", // not both
    "rating": "integer(1-10)",  // Updated rating range
    "text": "string"
}

Response (201): Created review object
```

#### Get Single Review
```
GET /api/reviews/{id}/

Response (200): Single review object
```

#### Update Review
```
PUT /api/reviews/{id}/
PATCH /api/reviews/{id}/  # For partial updates
Content-Type: application/json

{
    "rating": "integer(1-10)",  // Updated rating range
    "text": "string"
}

Response (200): Updated review object
```

#### Delete Review
```
DELETE /api/reviews/{id}/

Response (204): No content
```

### Genre Endpoints

#### List Genres
```
GET /api/genres/

Response (200):
[
    {
        "id": "integer",
        "name": "string"
    }
]
```

### System Endpoints

#### Health Check
```
GET /health/

Response (200):
{
    "status": "healthy",
    "database": "healthy",
    "cache": "healthy"
}
```

### Error Responses

All endpoints may return these error responses:

```
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

// Example: Submit a review
const submitReview = async (albumId, rating, text) => {
  // rating should be between 1 and 10
  const response = await fetch('/api/reviews/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      album_id: albumId,
      rating: rating,  // 1-10 rating
      text: text
    })
  });
  return response.json();
};
```

## Deployment

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

### AWS Deployment

1. Create AWS resources:
   - RDS PostgreSQL instance
   - ElastiCache Redis instance
   - Elastic Beanstalk environment

2. Configure environment variables in AWS console

3. Deploy:
```bash
eb init
eb create boomboxd-env
eb deploy
```

## Environment Variables

Required environment variables in `.env`:

```plaintext
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

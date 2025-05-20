# Boomboxd Backend API

A Django REST API for the Boomboxd music review platform. This API allows users to search for albums, view album details, write reviews, and manage their profiles.

## API Endpoints

### Authentication

#### Register a New User
```http
POST /api/accounts/register/
```
**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password",
    "bio": "Optional user bio",
    "avatar_url": "Optional avatar URL"
}
```
**Response (201):**
```json
{
    "username": "your_username",
    "bio": "Optional user bio",
    "avatar_url": "Optional avatar URL"
}
```

#### Login
```http
POST /api/accounts/login/
```
**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```
**Response (200):**
```json
{
    "username": "your_username",
    "bio": "User bio",
    "avatar_url": "Avatar URL"
}
```

### User Profile

#### Get User Profile
```http
GET /api/accounts/profile/
```
**Response (200):**
```json
{
    "username": "your_username",
    "bio": "User bio",
    "avatar_url": "Avatar URL"
}
```

#### Update User Profile
```http
PUT /api/accounts/profile/
```
**Request Body:**
```json
{
    "bio": "Updated bio",
    "avatar_url": "Updated avatar URL"
}
```
**Response (200):**
```json
{
    "username": "your_username",
    "bio": "Updated bio",
    "avatar_url": "Updated avatar URL"
}
```

### Album Operations

#### Search Albums
```http
GET /api/music/search/?q=search_term
```
**Response (200):**
```json
{
    "results": [
        {
            "discogs_id": "1234567",
            "title": "Album Title",
            "artist": "Artist Name",
            "year": 2024,
            "cover_image": "URL to album cover",
            "genres": ["Genre1", "Genre2"],
            "styles": ["Style1", "Style2"]
        }
    ]
}
```

#### Get Album Details
```http
GET /api/music/albums/{discogs_id}/
```
**Response (200):**
```json
{
    "id": 1,
    "title": "Album Title",
    "artist": "Artist Name",
    "year": 2024,
    "cover_url": "URL to album cover",
    "discogs_id": "1234567",
    "genres": ["Genre1", "Genre2"],
    "styles": ["Style1", "Style2"],
    "review_count": 10,
    "average_rating": 4.5,
    "exists_in_db": true,
    "reviews": [
        {
            "id": 1,
            "username": "reviewer",
            "rating": 5,
            "content": "Great album!",
            "created_at": "2024-03-20T12:00:00Z"
        }
    ]
}
```

#### Create Album Review
```http
POST /api/music/albums/{discogs_id}/review/
```
**Request Body:**
```json
{
    "rating": 5,
    "content": "This album is amazing!"
}
```
**Response (201):**
```json
{
    "id": 1,
    "username": "your_username",
    "rating": 5,
    "content": "This album is amazing!",
    "created_at": "2024-03-20T12:00:00Z"
}
```

### User Reviews

#### Get User's Reviews
```http
GET /api/accounts/users/{username}/reviews/
```
**Response (200):**
```json
[
    {
        "id": 1,
        "username": "username",
        "rating": 5,
        "content": "Review content",
        "created_at": "2024-03-20T12:00:00Z"
    }
]
```

## Authentication

The API uses session-based authentication. After logging in, include the session cookie in subsequent requests.

## Error Responses

The API returns appropriate HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Server Error

Error responses include a message:
```json
{
    "error": "Error message description"
}
```

## Rate Limiting

Currently, there are no rate limits implemented on the API endpoints.

## Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Start the development server: `python manage.py runserver`

The API will be available at `http://localhost:8000/`
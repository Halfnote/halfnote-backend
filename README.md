# Boomboxd API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the access token in the `Authorization` header:
```javascript
headers: {
  'Authorization': 'Bearer your_access_token_here',
  'Content-Type': 'application/json'
}
```

## Account Management

### Register a New User
```javascript
fetch('http://localhost:8000/api/accounts/register/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'your_username',
    password: 'your_password',
    bio: 'Optional bio',
    avatar_url: 'Optional avatar URL'
  })
})
.then(response => response.json())
.then(data => {
  // Store tokens
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
});
```

**Response (201):**
```json
{
  "username": "your_username",
  "bio": "Optional bio",
  "avatar_url": "Optional avatar URL",
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token"
}
```

### Login
```javascript
fetch('http://localhost:8000/api/accounts/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'your_username',
    password: 'your_password'
  })
})
.then(response => response.json())
.then(data => {
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
});
```

**Response (200):**
```json
{
  "username": "your_username",
  "bio": "User bio",
  "avatar_url": "Avatar URL",
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token"
}
```

## Music & Albums

### Search Albums
Search for albums using the Discogs database:

```javascript
fetch('http://localhost:8000/api/music/search/?q=Lorde+Melodrama', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  // Handle search results
  console.log(data.results);
});
```

**Response (200):**
```json
{
  "results": [
    {
      "discogs_id": "1196330",
      "title": "Melodrama",
      "artist": "Lorde",
      "year": 2017,
      "cover_image": "URL to album cover",
      "genres": ["Pop"],
      "styles": ["Indie Pop", "Synth-pop"]
    }
  ]
}
```

### Get Album Details
Get detailed information about an album, including its reviews:

```javascript
fetch('http://localhost:8000/api/music/albums/1196330/', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  console.log(data);
});
```

**Response (200):**
```json
{
  "album": {
    "id": "1196330",
    "title": "Melodrama",
    "artist": "Lorde",
    "year": 2017,
    "cover_url": "URL to album cover",
    "genres": ["Pop"],
    "styles": ["Indie Pop", "Synth-pop"],
    "review_count": 1,
    "average_rating": 8.0
  },
  "reviews": [
    {
      "id": 1,
      "username": "viv360",
      "rating": 8,
      "content": "A masterpiece of modern pop music",
      "created_at": "2024-03-20T12:00:00Z"
    }
  ],
  "exists_in_db": true
}
```

## Reviews

### Create a Review
```javascript
fetch('http://localhost:8000/api/music/albums/1196330/review/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    rating: 8,
    content: "A masterpiece of modern pop music"
  })
})
.then(response => response.json())
.then(data => {
  console.log(data);
});
```

**Response (201):**
```json
{
  "id": 1,
  "username": "viv360",
  "rating": 8,
  "content": "A masterpiece of modern pop music",
  "created_at": "2024-03-20T12:00:00Z"
}
```

### Get User's Reviews
```javascript
fetch('http://localhost:8000/api/accounts/users/viv360/reviews/', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  console.log(data);
});
```

**Response (200):**
```json
[
  {
    "id": 1,
    "username": "viv360",
    "rating": 8,
    "content": "A masterpiece of modern pop music",
    "created_at": "2024-03-20T12:00:00Z"
  }
]
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

```javascript
// Example error handling
fetch('http://localhost:8000/api/music/albums/1196330/review/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    rating: 8,
    content: "Review content"
  })
})
.then(response => {
  if (!response.ok) {
    throw response;
  }
  return response.json();
})
.catch(async error => {
  if (error instanceof Response) {
    const errorData = await error.json();
    console.error('API Error:', errorData.error);
  }
});
```

Common error responses:
```json
{
  "error": "Authentication required"
}
// Status: 401

{
  "error": "Album not found"
}
// Status: 404

{
  "error": "Invalid rating value"
}
// Status: 400
```

## Development Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
DISCOGS_CONSUMER_KEY=your_discogs_key
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## CORS Configuration

The API is configured to accept requests from all origins in development. For production, update the CORS settings in `settings.py` to specify allowed origins.
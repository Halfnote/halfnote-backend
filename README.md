# Boomboxd API Documentation

## Base URL
```
http://localhost:8000/api
```

---

## Authentication
All `/api/*` endpoints require a valid JWT access token in the `Authorization` header:

```
Authorization: Bearer <your_access_token>
```

If the token is missing or invalid, you will receive a `401 Unauthorized` error.

---

## Rate Limiting
Each IP address is limited to **5 requests per minute**. If you exceed this limit, you will receive a `429 Too Many Requests` error.

---

## Input Validation
All input is validated on the backend. If you send invalid or missing fields, you will receive a `400 Bad Request` response with details about the validation errors.

---

## Account Management

### Register a New User
```javascript
fetch('http://localhost:8000/api/accounts/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'your_username',
    password: 'your_password',
    bio: 'Optional bio',
    avatar_url: 'Optional avatar URL'
  })
})
.then(response => response.json())
.then(data => {
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
});
```

### Login
```javascript
fetch('http://localhost:8000/api/accounts/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
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

---

## User Profile & Social

### Get Your Profile
```javascript
fetch('http://localhost:8000/api/accounts/profile/', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') }
})
.then(res => res.json())
.then(console.log);
```

### Get Another User's Profile
```javascript
fetch('http://127.0.0.1:8000/api/accounts/profile/otheruser/', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') }
})
.then(res => res.json())
.then(console.log);
```

### Update Your Profile
```javascript
fetch('http://127.0.0.1:8000/api/accounts/profile/update/', {
  method: 'PUT',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ bio: 'New bio', avatar_url: 'https://...' })
})
.then(res => res.json())
.then(console.log);
```

### Follow/Unfollow Users
```javascript
// Follow
fetch('http://127.0.0.1:8000/api/accounts/follow/otheruser/', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') }
});
// Unfollow
fetch('http://127.0.0.1:8000/api/accounts/unfollow/otheruser/', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') }
});
```

### Get Followers/Following
```javascript
// Followers
fetch('http://127.0.0.1:8000/api/accounts/followers/otheruser/', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') }
})
.then(res => res.json())
.then(console.log);
// Following
fetch('http://127.0.0.1:8000/api/accounts/following/otheruser/', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') }
})
.then(res => res.json())
.then(console.log);
```

---

## Music & Albums

### Search Albums
```javascript
fetch('http://127.0.0.1:8000/api/music/search/?q=Lorde+Melodrama', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') }
})
.then(res => res.json())
.then(console.log);
```

### Get Album Details
```javascript
fetch('http://127.0.0.1:8000/api/music/albums/1196330/', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') }
})
.then(res => res.json())
.then(console.log);
```

---

## Reviews

### Create a Review
```javascript
fetch('http://127.0.0.1:8000/api/music/albums/1196330/review/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ rating: 8, content: 'A masterpiece of modern pop music' })
})
.then(res => res.json())
.then(console.log);
```

### Get User's Reviews
```javascript
fetch('http://127.0.0.1:8000/api/accounts/users/viv360/reviews/', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') }
})
.then(res => res.json())
.then(console.log);
```

---

## Error Handling

All endpoints return appropriate HTTP status codes and error messages. Example:

```javascript
fetch('http://127.0.0.1:8000/api/music/albums/1196330/review/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ rating: 8, content: 'Review content' })
})
.then(response => {
  if (!response.ok) throw response;
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

{
  "error": "Rate limit exceeded. Please try again later."
}
// Status: 429
```

---

## Environment Variables
Sensitive information such as API keys and tokens must be set via environment variables. Do not hardcode secrets in the codebase.

---

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
DISCOGS_CONSUMER_SECRET=your_discogs_secret
DISCOGS_TOKEN=your_discogs_token
```
4. Run migrations:
```bash
python manage.py migrate
```
5. Start the development server:
```bash
python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000/`

---

## CORS Configuration
The API is configured to accept requests from all origins in development. For production, update the CORS settings in `settings.py` to specify allowed origins.
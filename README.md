# Boomboxd Backend

A Django-based backend service for the Boomboxd music rating platform.

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from `.env.template` and fill in your values.

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

- `/api/albums/` - Album management
- `/api/singles/` - Single management
- `/api/reviews/` - Review management
- `/api/auth/register/` - User registration
- `/api/auth/login/` - User login
- `/api/auth/refresh/` - Refresh JWT token
- `/api/profile/` - User profile management
- `/health/` - Health check endpoint

## External Services

- MusicBrainz - Primary music metadata source
- Spotify - Additional metadata and streaming links
- YouTube - Music video links

## Caching

Redis is used for caching frequently accessed data:
- Search results
- Album/Single details
- User profiles

## Rate Limiting

- Anonymous users: 100 requests per day
- Authenticated users: 1000 requests per day 
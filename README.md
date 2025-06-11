# Halfnote API - Letterboxd for Music

A Django-based API for music reviews and social features, inspired by Letterboxd. Users can discover music, write reviews, follow others, and interact with a community of music lovers.

## 🚀 Features

- **User Authentication & Profiles**: JWT-based auth with customizable user profiles
- **Music Discovery**: Search albums via Discogs API integration
- **Review System**: Rate albums (1-10), write reviews, pin favorites
- **Social Features**: Follow users, activity feeds, comments
- **Genre Tagging**: User-assigned genres for personalized organization
- **Comments & Interactions**: Like reviews, comment on posts

## 🔗 Base URL
```
http://localhost:8000/api
```

## 🔑 Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

### Register
**POST** `/api/accounts/register/`

```javascript
const authToken = await fetch('/api/accounts/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'musiclover',
    email: 'user@example.com',
    password: 'securepassword123',
    bio: 'Music enthusiast from San Francisco',
    favorite_genres: ['Jazz', 'Electronic']
  })
})
.then(res => res.json())
.then(data => {
  localStorage.setItem('authToken', data.access);
  localStorage.setItem('refreshToken', data.refresh);
  return data.access;
});
```

### Login
**POST** `/api/accounts/login/`

```javascript
const authToken = await fetch('/api/accounts/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'musiclover',
    password: 'securepassword123'
  })
})
.then(res => res.json())
.then(data => {
  localStorage.setItem('authToken', data.access);
  localStorage.setItem('refreshToken', data.refresh);
  return data.access;
});
```

### Refresh Token
**POST** `/api/accounts/token/refresh/`

```javascript
const newToken = await fetch('/api/accounts/token/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    refresh: localStorage.getItem('refreshToken')
  })
})
.then(res => res.json())
.then(data => {
  localStorage.setItem('authToken', data.access);
  return data.access;
});
```

## 👤 User Profiles & Social

### Get Current User Profile
**GET** `/api/accounts/profile/`

```javascript
const userProfile = await fetch('/api/accounts/profile/', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Response includes:
// { id, username, email, bio, avatar, favorite_genres, followers_count, following_count, review_count }
```

### Get Another User's Profile  
**GET** `/api/accounts/users/{username}/`

```javascript
const userProfile = await fetch('/api/accounts/users/viv360/', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());
```

### Update Profile
**PUT** `/api/accounts/profile/`

```javascript
await fetch('/api/accounts/profile/', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    bio: 'Jazz enthusiast and vinyl collector',
    favorite_genres: ['Jazz', 'Blues', 'Soul']
  })
});
```

### Follow/Unfollow Users
**POST** `/api/accounts/users/{username}/follow/`
**POST** `/api/accounts/users/{username}/unfollow/`

```javascript
// Follow a user
await fetch('/api/accounts/users/viv360/follow/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${authToken}` }
});

// Unfollow a user
await fetch('/api/accounts/users/viv360/unfollow/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${authToken}` }
});
```

### Get User's Reviews
**GET** `/api/accounts/users/{username}/reviews/`

```javascript
const userReviews = await fetch('/api/accounts/users/viv360/reviews/', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Returns array of reviews with album info, ratings, content, genres, etc.
```

## 🎵 Music & Albums

### Search Albums
**GET** `/api/music/search/?q={query}`

```javascript
const searchResults = await fetch('/api/music/search/?q=Radiohead+OK+Computer', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Returns array of albums from Discogs
// { discogs_id, title, artist, year, cover_image, formats }
```

### Get Album Details
**GET** `/api/music/albums/{discogs_id}/`

```javascript
const albumDetails = await fetch('/api/music/albums/1123456/', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Detailed album info including tracklist, credits, user reviews
```

### Get Available Genres
**GET** `/api/music/genres/`

```javascript
const genres = await fetch('/api/music/genres/', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Returns: { genres: [{ id: 1, name: "Jazz" }, ...] }
```

## ⭐ Reviews & Ratings

### Create a Review
**POST** `/api/music/albums/{discogs_id}/review/`

```javascript
const newReview = await fetch('/api/music/albums/1123456/review/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    rating: 9,
    content: 'A groundbreaking album that redefined alternative rock. Every track is perfectly crafted.',
    genres: ['Alternative Rock', 'Experimental']
  })
})
.then(res => res.json());
```

### Edit a Review
**PUT** `/api/music/reviews/{review_id}/`

```javascript
await fetch('/api/music/reviews/123/', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    rating: 10,
    content: 'Updated: This album is absolutely perfect. A masterpiece.',
    genres: ['Alternative Rock', 'Art Rock', 'Experimental']
  })
});
```

### Delete a Review
**DELETE** `/api/music/reviews/{review_id}/`

```javascript
await fetch('/api/music/reviews/123/', {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${authToken}` }
});
```

### Pin/Unpin a Review
**POST** `/api/music/reviews/{review_id}/pin/`

```javascript
// Toggles pin status
await fetch('/api/music/reviews/123/pin/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${authToken}` }
});
```

### Like/Unlike a Review
**POST** `/api/music/reviews/{review_id}/like/`

```javascript
// Toggles like status
await fetch('/api/music/reviews/123/like/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${authToken}` }
});
```

## 💬 Comments

### Get Review Comments
**GET** `/api/music/reviews/{review_id}/comments/?offset={offset}&limit={limit}`

```javascript
const comments = await fetch('/api/music/reviews/123/comments/?offset=0&limit=10', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Returns: { comments: [...], has_more: boolean }
```

### Add a Comment
**POST** `/api/music/reviews/{review_id}/comments/`

```javascript
const newComment = await fetch('/api/music/reviews/123/comments/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: 'Great review! I totally agree about the production quality.'
  })
})
.then(res => res.json());
```

## 📈 Activity Feed

### Get Activity Feed
**GET** `/api/music/activity/`

```javascript
const activityFeed = await fetch('/api/music/activity/', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Returns recent activity from followed users
// Includes reviews, likes, comments with full context
```

## 🎨 Frontend Integration Examples

### Complete Review Management Component

```javascript
class ReviewManager {
  constructor(authToken) {
    this.authToken = authToken;
    this.baseURL = '/api';
  }

  async createReview(discogsId, rating, content, genres = []) {
    return fetch(`${this.baseURL}/music/albums/${discogsId}/review/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.authToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ rating, content, genres })
    }).then(res => res.json());
  }

  async editReview(reviewId, rating, content, genres = []) {
    return fetch(`${this.baseURL}/music/reviews/${reviewId}/`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${this.authToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ rating, content, genres })
    }).then(res => res.json());
  }

  async togglePin(reviewId) {
    return fetch(`${this.baseURL}/music/reviews/${reviewId}/pin/`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.authToken}` }
    }).then(res => res.json());
  }

  async deleteReview(reviewId) {
    return fetch(`${this.baseURL}/music/reviews/${reviewId}/`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${this.authToken}` }
    });
  }
}

// Usage
const reviewManager = new ReviewManager(localStorage.getItem('authToken'));
await reviewManager.createReview(1123456, 9, 'Amazing album!', ['Jazz', 'Fusion']);
```

### Comment System with Pagination

```javascript
class CommentSystem {
  constructor(authToken) {
    this.authToken = authToken;
    this.comments = new Map(); // Cache comments by review ID
  }

  async loadComments(reviewId, offset = 0, limit = 10) {
    const response = await fetch(`/api/music/reviews/${reviewId}/comments/?offset=${offset}&limit=${limit}`, {
      headers: { 'Authorization': `Bearer ${this.authToken}` }
    });
    
    const data = await response.json();
    
    // Cache or append to existing comments
    if (offset === 0) {
      this.comments.set(reviewId, data.comments);
    } else {
      const existing = this.comments.get(reviewId) || [];
      this.comments.set(reviewId, [...existing, ...data.comments]);
    }
    
    return data;
  }

  async addComment(reviewId, content) {
    const newComment = await fetch(`/api/music/reviews/${reviewId}/comments/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.authToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content })
    }).then(res => res.json());

    // Add to cache
    const existing = this.comments.get(reviewId) || [];
    this.comments.set(reviewId, [newComment, ...existing]);
    
    return newComment;
  }

  renderComments(reviewId, containerId) {
    const comments = this.comments.get(reviewId) || [];
    const container = document.getElementById(containerId);
    
    container.innerHTML = comments.map(comment => `
      <div class="comment">
        <div class="comment-header">
          <strong>${comment.username}</strong>
          <span class="comment-date">${new Date(comment.created_at).toLocaleDateString()}</span>
        </div>
        <div class="comment-content">${comment.content}</div>
      </div>
    `).join('');
  }
}

// Usage
const commentSystem = new CommentSystem(localStorage.getItem('authToken'));
await commentSystem.loadComments(123);
commentSystem.renderComments(123, 'comments-container');
```

### Activity Feed Component

```javascript
class ActivityFeed {
  constructor(authToken) {
    this.authToken = authToken;
  }

  async loadActivity() {
    return fetch('/api/music/activity/', {
      headers: { 'Authorization': `Bearer ${this.authToken}` }
    }).then(res => res.json());
  }

  renderActivity(activities, containerId) {
    const container = document.getElementById(containerId);
    
    container.innerHTML = activities.map(activity => {
      const review = activity.review_details;
      return `
        <div class="activity-item">
          <div class="activity-header">
            <strong>${activity.username}</strong> reviewed
            <strong>${review.album_title}</strong> by ${review.album_artist}
          </div>
          <div class="activity-content">
            <img src="${review.album_cover}" alt="${review.album_title}" class="activity-album-cover">
            <div class="activity-details">
              <div class="activity-rating">${review.rating}/10</div>
              <div class="activity-review">"${review.content}"</div>
              <div class="activity-meta">
                ${new Date(activity.created_at).toLocaleDateString()}
                ${review.user_genres?.length ? ' • ' + review.user_genres.map(g => g.name).join(', ') : ''}
              </div>
              <button onclick="showComments(${review.id})" class="comments-btn">
                💬 ${review.comments_count} comments
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }
}

// Usage
const activityFeed = new ActivityFeed(localStorage.getItem('authToken'));
const activities = await activityFeed.loadActivity();
activityFeed.renderActivity(activities, 'activity-container');
```

## 📱 Frontend Pages

The API serves several frontend pages with full functionality:

- **`/`** - Landing page with authentication
- **`/users/{username}/`** - User profile with reviews, pinned content, self-management
- **`/activity/`** - Social activity feed
- **`/search/`** - Music search and discovery

## 🔧 Development Setup

1. **Clone and Install**
```bash
git clone <repository>
cd boomboxd-backend
pip install -r requirements.txt
```

2. **Environment Variables** (`.env`)
```env
DJANGO_SECRET_KEY=your_secret_key_here
DEBUG=True
DISCOGS_CONSUMER_KEY=your_discogs_key
DISCOGS_CONSUMER_SECRET=your_discogs_secret
DISCOGS_TOKEN=your_discogs_token
```

3. **Database Setup**
```bash
python manage.py migrate
python manage.py createsuperuser
```

4. **Run Development Server**
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## ⚠️ Error Handling

All endpoints return appropriate HTTP status codes:

- **200** - Success
- **201** - Created successfully  
- **400** - Bad request (validation errors)
- **401** - Authentication required
- **403** - Permission denied
- **404** - Resource not found
- **429** - Rate limit exceeded

Example error responses:
```json
{
  "error": "Authentication required"
}

{
  "error": "Album not found on Discogs", 
  "status": 404
}

{
  "detail": "Rating must be between 1 and 10",
  "field": "rating"
}
```

### Frontend Error Handling

```javascript
async function apiCall(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || error.detail || 'API request failed');
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error.message);
    
    // Handle specific error cases
    if (error.message.includes('Authentication')) {
      // Redirect to login or refresh token
      window.location.href = '/';
    }
    
    throw error;
  }
}
```

## 🎯 Key Features Summary

- **Authentication**: JWT-based with refresh tokens
- **Music Data**: Discogs API integration for comprehensive album database
- **Reviews**: 1-10 ratings with rich text content and custom genre tagging  
- **Social**: Follow users, activity feeds, review interactions
- **Comments**: Threaded discussions on reviews with pagination
- **Profile Management**: User profiles with pinned reviews and statistics
- **Real-time UI**: Dynamic frontend with immediate updates
- **Mobile-Friendly**: Responsive design optimized for all devices

---

Built with Django, PostgreSQL, and modern JavaScript. Inspired by Letterboxd's elegant approach to media discovery and social sharing.
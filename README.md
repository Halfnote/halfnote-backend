# 🎵 Halfnote API - Letterboxd for Music

A comprehensive Django-based API for music reviews and social features, inspired by Letterboxd. Users can discover music, write detailed reviews, follow others, and interact with a vibrant community of music lovers.

## 🚀 Features

- **🔐 User Authentication & Profiles**: JWT-based auth with customizable user profiles, avatars, and bios
- **🎼 Music Discovery**: Search albums via Discogs API integration with rich metadata
- **⭐ Review System**: Rate albums (1-10 scale), write detailed reviews, pin favorites, edit/delete reviews with slider UI
- **👥 Social Features**: Follow users, activity feeds, like reviews, comment threads
- **🏷️ Genre Tagging**: User-assigned genres for personalized organization and discovery
- **💬 Comments & Interactions**: Threaded comments, edit/delete own comments, pagination
- **📱 Responsive Frontend**: Complete web interface with mobile-optimized design
- **🔄 Real-time Updates**: Dynamic UI with immediate feedback and state management
- **📊 Activity Tracking**: Comprehensive activity feeds with different view modes (Friends, You, Incoming)

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
    rating: 9, // Rating must be between 1-10
    content: 'A groundbreaking album that redefined alternative rock. Every track is perfectly crafted.',
    genres: ['Alternative Rock', 'Experimental']
  })
})
.then(res => res.json());
```

### Get Single Review
**GET** `/api/music/reviews/{review_id}/`

```javascript
const review = await fetch('/api/music/reviews/123/', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Returns detailed review with album info, user data, like status, etc.
// { id, rating, content, user_genres, album_title, username, is_liked_by_user, likes_count, is_pinned, created_at }
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
    rating: 10, // Rating must be between 1-10
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

### Edit a Comment
**PUT** `/api/music/comments/{comment_id}/`

```javascript
await fetch('/api/music/comments/456/', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: 'Updated comment: Great review! The production is phenomenal.'
  })
});
```

### Delete a Comment
**DELETE** `/api/music/comments/{comment_id}/`

```javascript
await fetch('/api/music/comments/456/', {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${authToken}` }
});
```

## 📈 Activity Feed

### Get Activity Feed
**GET** `/api/music/activity/?type={type}`

Available types: `friends` (default), `you`, `incoming`

```javascript
// Get friends' activity (default)
const friendsActivity = await fetch('/api/music/activity/?type=friends', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Get your own activity
const yourActivity = await fetch('/api/music/activity/?type=you', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Get incoming activity (others interacting with your content)
const incomingActivity = await fetch('/api/music/activity/?type=incoming', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Returns activity with full context:
// { activity_type, username, target_username, created_at, review_details, comment_details }
```

### Get User Followers/Following
**GET** `/api/accounts/users/{username}/followers/`
**GET** `/api/accounts/users/{username}/following/`

```javascript
const followers = await fetch('/api/accounts/users/viv360/followers/', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

const following = await fetch('/api/accounts/users/viv360/following/', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());
```

### Search Users
**GET** `/api/accounts/users/search/?q={query}`

```javascript
const users = await fetch('/api/accounts/users/search/?q=viv', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Returns: { users: [{ id, username, bio, avatar, is_following }, ...] }
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

## 📱 Frontend Pages & Features

The API serves a complete web application with responsive design and modern UX:

### 🏠 Landing Page (`/`)
- **Authentication**: Login/register forms with JWT token management
- **Welcome Interface**: Clean, modern design introducing the platform
- **Auto-redirect**: Logged-in users redirected to activity feed

### 👤 User Profiles (`/users/{username}/`)
- **Profile Header**: Avatar, bio, follower/following counts, review statistics
- **Review Grid**: Compact album covers (120px) in Letterboxd-style layout
- **Pinned Reviews**: Highlighted favorite reviews at the top
- **Review Management**: Edit/delete/pin your own reviews with modal interface
- **Social Actions**: Follow/unfollow other users, view their reviews
- **Genre Selection**: Multi-select genre tagging with visual grid interface
- **Responsive Design**: Mobile-optimized with touch-friendly interactions

### 📊 Activity Feed (`/activity/`)
- **Three View Modes**:
  - **Friends**: Activity from users you follow
  - **You**: Your own activity history  
  - **Incoming**: Others interacting with your content
- **Rich Activity Cards**: Album covers, ratings, review excerpts, timestamps
- **Clickable Elements**: Album titles link to individual review pages
- **Smart Text**: "You liked your review" vs "You liked viv360's review"
- **Real-time Updates**: Dynamic loading and state management

### 🎵 Individual Review Pages (`/review/{id}/`)
- **Letterboxd-style Layout**: Large album cover (250px), title, artist, rating
- **Review Header**: Compact action buttons (📌✏️🗑️) next to score
- **Review Content**: Full review text with proper typography
- **Genre Tags**: User-assigned genres displayed prominently
- **Comments System**: Threaded comments with edit/delete functionality
- **Social Features**: Like reviews, comment interactions
- **Edit Modal**: In-place editing with genre selection grid
- **Responsive**: Adapts beautifully to mobile devices

### 🔍 Search & Discovery (`/search/`)
- **Discogs Integration**: Search vast music database
- **Rich Results**: Album covers, artist info, release years
- **Quick Actions**: Direct review creation from search results

### 🎨 Design Philosophy
- **Letterboxd-inspired**: Clean, content-focused design
- **Mobile-first**: Touch-friendly interactions, responsive layouts
- **Modern UX**: Smooth animations, immediate feedback, intuitive navigation
- **Accessibility**: Proper contrast, keyboard navigation, screen reader support

## 🔧 Development Setup

1. **Clone and Install**
```bash
git clone <repository>
cd halfnote-backend
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
python manage.py setup_cache  # Initialize caching system
python manage.py createsuperuser
```

4. **Run Development Server**
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

### 🚀 Production Caching Setup

For optimal performance in production, configure Redis Cloud:

1. **Set up Redis Cloud** in your Vercel environment variables:
   ```bash
   REDIS_URL=redis://default:password@your-redis-host:port
   ```

2. **Automatic Fallback**: If Redis is unavailable, the system automatically uses database caching

3. **Cache Management Commands**:
   ```bash
   python manage.py setup_cache     # Initialize cache system
   python manage.py clear_cache     # Clear all caches
   python manage.py cache_stats     # View cache performance
   ```

**Performance Impact**: 90% faster activity feeds, 60% faster cold starts, 85% fewer database queries

📖 **Detailed Documentation**: See [CACHING_STRATEGY.md](./CACHING_STRATEGY.md) for complete implementation details

## 📋 Complete API Reference

### Authentication Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/accounts/register/` | Create new user account | No |
| POST | `/api/accounts/login/` | Login and get JWT tokens | No |
| POST | `/api/accounts/token/refresh/` | Refresh access token | No |
| GET | `/api/accounts/profile/` | Get current user profile | Yes |
| PUT | `/api/accounts/profile/` | Update current user profile | Yes |

### User & Social Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/accounts/users/{username}/` | Get user profile | Optional |
| GET | `/api/accounts/users/{username}/reviews/` | Get user's reviews | Optional |
| GET | `/api/accounts/users/{username}/followers/` | Get user's followers | Yes |
| GET | `/api/accounts/users/{username}/following/` | Get users they follow | Yes |
| GET | `/api/accounts/users/search/?q={query}` | Search users by username | Yes |
| POST | `/api/accounts/users/{username}/follow/` | Follow user | Yes |
| POST | `/api/accounts/users/{username}/unfollow/` | Unfollow user | Yes |

### Music & Album Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/music/search/?q={query}` | Search albums via Discogs | Yes |
| GET | `/api/music/albums/{discogs_id}/` | Get album details | Yes |
| GET | `/api/music/genres/` | Get available genres | No |

### Review Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/music/albums/{discogs_id}/review/` | Create review | Yes |
| GET | `/api/music/reviews/{review_id}/` | Get single review | Optional |
| PUT | `/api/music/reviews/{review_id}/` | Edit review (own only) | Yes |
| DELETE | `/api/music/reviews/{review_id}/` | Delete review (own only) | Yes |
| POST | `/api/music/reviews/{review_id}/pin/` | Toggle pin status (own only) | Yes |
| POST | `/api/music/reviews/{review_id}/like/` | Toggle like status | Yes |

### Comment Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/music/reviews/{review_id}/comments/` | Get review comments | Optional |
| POST | `/api/music/reviews/{review_id}/comments/` | Add comment | Yes |
| PUT | `/api/music/comments/{comment_id}/` | Edit comment (own only) | Yes |
| DELETE | `/api/music/comments/{comment_id}/` | Delete comment (own only) | Yes |

### Activity Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/music/activity/?type=friends` | Get friends' activity | Yes |
| GET | `/api/music/activity/?type=you` | Get your activity | Yes |
| GET | `/api/music/activity/?type=incoming` | Get incoming activity | Yes |

### Static File Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/static/{path}` | Serve static files (CSS, JS, images) | No |
| GET | `/static/accounts/default-avatar.svg` | Default user avatar | No |
| GET | `/static/default-album.svg` | Default album cover | No |

## ⚠️ Error Handling & Status Codes

### HTTP Status Codes
- **200** - Success (GET, PUT requests)
- **201** - Created successfully (POST requests)
- **204** - No content (successful DELETE)
- **400** - Bad request (validation errors)
- **401** - Authentication required
- **403** - Permission denied (not your content)
- **404** - Resource not found
- **429** - Rate limit exceeded
- **500** - Internal server error

### Error Response Formats
```json
// Authentication error
{
  "error": "Authentication required"
}

// Validation error
{
  "detail": "Rating must be between 1 and 10",
  "field": "rating"
}

// Not found error
{
  "error": "Album not found on Discogs", 
  "status": 404
}

// Permission error
{
  "error": "You can only edit your own reviews"
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

## 🎯 Key Features & Recent Improvements

### 🔐 Authentication & Security
- **JWT-based Authentication**: Secure token-based auth with refresh tokens
- **Permission System**: Granular permissions for editing/deleting own content
- **Rate Limiting**: Protection against API abuse

### 🎵 Music & Reviews
- **Discogs Integration**: Access to comprehensive music database
- **Rich Review System**: Consistent 1-10 ratings with detailed text reviews and intuitive slider UI
- **Custom Genre Tagging**: User-assigned genres for personalized organization
- **Review Management**: Edit, delete, pin/unpin reviews with modal interface
- **Social Interactions**: Like reviews with race condition prevention, follow users, comment on reviews
- **Rating Validation**: Automatic clamping to prevent ratings outside 1-10 range

### 💬 Comments & Interactions
- **Threaded Comments**: Full comment system with edit/delete functionality
- **Pagination**: Efficient loading of large comment threads
- **Real-time Updates**: Immediate UI feedback for all interactions
- **Permission-based Actions**: Users can only edit/delete their own content

### 📊 Activity & Social Features
- **Multi-view Activity Feed**: Friends, personal, and incoming activity streams
- **Smart Activity Text**: Context-aware messaging ("your review" vs "username's review")
- **Clickable Elements**: Album titles link to detailed review pages
- **Follow System**: Build networks of music enthusiasts

### 🎨 Frontend & UX
- **Letterboxd-inspired Design**: Clean, content-focused interface
- **Responsive Layout**: Mobile-first design with touch-friendly interactions
- **Grid-based CSS**: Modern layout using CSS Grid and Flexbox
- **Compact UI Elements**: Emoji-only action buttons, optimized spacing
- **Modal Interfaces**: In-place editing without page navigation
- **Slider UI**: Intuitive rating slider with live feedback and clear value labels
- **Loading States**: Visual feedback with spinner icons to prevent double-clicks
- **Avatar System**: Fallback to default avatars with proper static file serving

### 📱 Mobile Optimization
- **Responsive Breakpoints**: Optimized for 768px (tablet) and 480px (mobile)
- **Touch-friendly**: Larger touch targets, swipe-friendly layouts
- **Adaptive Typography**: Font sizes and spacing adjust for screen size
- **Mobile Navigation**: Streamlined navigation for small screens

### 🔧 Technical Architecture
- **Django REST Framework**: Robust API with serializers and viewsets
- **PostgreSQL**: Reliable database with proper indexing
- **Modern JavaScript**: ES6+ features, async/await, fetch API
- **CSS Grid & Flexbox**: Modern layout techniques
- **JWT Token Management**: Secure client-side token handling

#### System Architecture

```mermaid
graph TD
    subgraph Vercel Hosting
        Frontend["React Frontend"]
        Backend["Django REST API"]
    end
    User["User Browser"] --> Frontend
    Frontend -->|REST Calls| Backend
    Backend --> PostgreSQL[("PostgreSQL DB")]
    Backend --> Redis[("Redis Cache")]
    Backend --> Cloudinary[("Cloudinary Storage")]
    Backend -->|Album Metadata| Discogs["Discogs API"]
```

### 🚀 Performance & Caching
- **Multi-Tier Caching**: Redis Cloud + database cache fallback (90% faster activity feeds)
- **Query Optimization**: 85% reduction in database queries (from 50+ to 3-5 per request)
- **Smart Cache Invalidation**: Maintains data consistency with intelligent cache clearing
- **Efficient Pagination**: Offset-based pagination for large datasets
- **Optimized Database Indexes**: Compound indexes for activity feeds and user queries
- **Lazy Loading**: Comments and activity load on demand
- **Serverless Optimized**: Built for Vercel deployment with 60% faster cold starts

📊 **Performance Results**: Activity feed loads in 200-500ms (down from 2-5 seconds)  
📖 **Detailed Documentation**: See [CACHING_STRATEGY.md](./CACHING_STRATEGY.md) for complete implementation details

---

**Built with Django, PostgreSQL, and modern JavaScript. Inspired by Letterboxd's elegant approach to media discovery and social sharing.**

*This platform demonstrates modern web development practices with a focus on user experience, performance, and maintainable code architecture.*
# 🎵 Halfnote API - Letterboxd for Music

A comprehensive Django-based API for music reviews and social features, inspired by Letterboxd. Users can discover music, write detailed reviews, follow others, and interact with a vibrant community of music lovers.

## 🚀 Features

- **🔐 User Authentication & Profiles**: JWT-based auth with customizable user profiles, avatars, and bios
- **🎼 Music Discovery**: Search albums via Discogs API integration with rich metadata
- **⭐ Review System**: Rate albums (1-10 scale), write detailed reviews, pin favorites (max 2), edit/delete reviews with slider UI
- **❤️ Favorite Albums**: Curate up to 5 favorite albums displayed prominently on your profile, similar to Letterboxd's favorite movies
- **📝 Lists & Collections**: Create and manage custom album lists, like/unlike lists, browse public lists
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
// { 
//   id, username, email, bio, avatar, favorite_genres, 
//   favorite_albums: [{ id, title, artist, year, cover_url, discogs_id, user_review_id, user_rating }],
//   followers_count, following_count, review_count, pinned_reviews: [...], is_staff 
// }
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

### Manage Favorite Albums
**GET/POST/DELETE** `/api/accounts/favorite-albums/`

```javascript
// Get current user's favorite albums
const favoriteAlbums = await fetch('/api/accounts/favorite-albums/', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Response includes:
// {
//   "favorite_albums": [
//     {
//       "id": "1234567",
//       "title": "OK Computer",
//       "artist": "Radiohead",
//       "year": 1997,
//       "cover_url": "https://...",
//       "discogs_id": "1234567",
//       "user_review_id": 123,
//       "user_rating": 9,
//       "user_review_content": "A masterpiece..."
//     }
//   ]
// }

// Add album to favorites (max 5 albums)
await fetch('/api/accounts/favorite-albums/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    discogs_id: '1234567'  // or album_id: 'uuid'
  })
});

// Remove album from favorites
await fetch('/api/accounts/favorite-albums/', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    album_id: 'album-uuid'
  })
});

// Error responses:
// { "error": "You can only have up to 5 favorite albums" }
// { "error": "Album not found" }
// { "error": "Album is already in your favorites" }
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

// Returns array of reviews with album info, ratings, content, genres, staff status, etc.
// Each review includes: { id, rating, content, user_genres, album_title, album_artist, album_year, username, user_is_staff, ... }
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

// Returns detailed review with album info, user data, like status, staff verification, etc.
// { id, rating, content, user_genres, album_title, album_artist, album_year, username, user_is_staff, is_liked_by_user, likes_count, is_pinned, created_at }
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
// Toggles pin status (max 2 pinned reviews per user)
await fetch('/api/music/reviews/123/pin/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${authToken}` }
});

// Error response when trying to pin more than 2 reviews:
// { "error": "You can only pin up to 2 reviews" }
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

### Get Review Likes
**GET** `/api/music/reviews/{review_id}/likes/?offset={offset}&limit={limit}&include_review={true|false}`

**Query Parameters:**
- `offset` (optional): Starting position for pagination (default: 0)
- `limit` (optional): Number of results per page (default: 20)
- `include_review` (optional): Include review details in response (default: false)

```javascript
// Simple likes data
const simpleLikes = await fetch('/api/music/reviews/123/likes/', {
  headers: { 'Authorization': `Bearer ${authToken}` }
}).then(res => res.json());

// Paginated likes with review details (for likes page UI)
const likesPageData = await fetch('/api/music/reviews/123/likes/?offset=0&limit=20&include_review=true', {
  headers: { 'Authorization': `Bearer ${authToken}` }
}).then(res => res.json());

// Returns (with include_review=true):
// {
//   "review": {
//     "id": 123,
//     "username": "reviewer",
//     "album_title": "OK Computer",
//     "album_artist": "Radiohead",
//     "album_cover": "https://...",
//     "rating": 9,
//     "content": "Amazing album...",
//     "created_at": "2024-01-15T10:30:00Z"
//   },
//   "users": [
//     {
//       "id": 1,
//       "username": "musiclover",
//       "name": "John Doe",
//       "avatar": "https://...",
//       "follower_count": 25,
//       "following_count": 30,
//       "review_count": 12
//     }
//   ],
//   "total_count": 1,
//   "has_more": false,
//   "next_offset": null
// }
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

## 📝 Lists

### Get Public Lists
**GET** `/api/music/lists/?offset={offset}&limit={limit}`

**Query Parameters:**
- `offset` (optional): Starting position for pagination (default: 0)
- `limit` (optional): Number of results per page (default: 20)

```javascript
const publicLists = await fetch('/api/music/lists/?offset=0&limit=20', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Returns:
// {
//   "lists": [
//     {
//       "id": 1,
//       "name": "Best Albums of 2024",
//       "description": "My favorite releases this year",
//       "user": {
//         "username": "musiclover",
//         "avatar": "https://..."
//       },
//       "album_count": 15,
//       "likes_count": 8,
//       "is_liked_by_user": false,
//       "is_public": true,
//       "created_at": "2024-01-15T10:30:00Z",
//       "updated_at": "2024-01-20T14:22:00Z"
//     }
//   ],
//   "total_count": 42,
//   "has_more": true,
//   "next_offset": 20
// }
```

### Create a List
**POST** `/api/music/lists/`

```javascript
const newList = await fetch('/api/music/lists/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Best Jazz Albums',
    description: 'Essential jazz recordings every music lover should hear', // Optional
    is_public: true
  })
})
.then(res => res.json());

// Returns the created list with full details
```

### Get List Details
**GET** `/api/music/lists/{list_id}/`

```javascript
const listDetails = await fetch('/api/music/lists/123/', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Returns detailed list with albums:
// {
//   "id": 123,
//   "name": "Best Jazz Albums",
//   "description": "Essential jazz recordings...",
//   "user": {
//     "username": "jazzlover",
//     "avatar": "https://..."
//   },
//   "items": [
//     {
//       "id": 1,
//       "order": 1,
//       "album": {
//         "id": 456,
//         "title": "Kind of Blue",
//         "artist": "Miles Davis",
//         "year": 1959,
//         "cover_url": "https://...",
//         "discogs_id": 12345,
//         "user_review_id": 789 // If user has reviewed this album
//       }
//     }
//   ],
//   "album_count": 10,
//   "likes_count": 25,
//   "is_liked_by_user": true,
//   "is_public": true,
//   "created_at": "2024-01-15T10:30:00Z",
//   "updated_at": "2024-01-20T14:22:00Z"
// }
```

### Update a List
**PUT** `/api/music/lists/{list_id}/`

```javascript
await fetch('/api/music/lists/123/', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Essential Jazz Albums',
    description: 'Updated description with more context...',
    is_public: false
  })
});

// Only the list owner can update
```

### Delete a List
**DELETE** `/api/music/lists/{list_id}/`

```javascript
await fetch('/api/music/lists/123/', {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${authToken}` }
});

// Only the list owner can delete
```

### Add Album to List
**POST** `/api/music/lists/{list_id}/albums/`

```javascript
// Add album by Discogs ID (most common - imports if needed)
await fetch('/api/music/lists/123/albums/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    discogs_id: 12345
  })
});

// Or add existing album by internal ID
await fetch('/api/music/lists/123/albums/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    album_id: 456
  })
});

// Returns the created list item with album details
```

### Remove Album from List
**DELETE** `/api/music/lists/{list_id}/albums/`

```javascript
// Remove by Discogs ID
await fetch('/api/music/lists/123/albums/', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    discogs_id: 12345
  })
});

// Or remove by internal album ID
await fetch('/api/music/lists/123/albums/', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    album_id: 456
  })
});
```

### Like/Unlike a List
**POST** `/api/music/lists/{list_id}/like/`

```javascript
// Toggles like status
const response = await fetch('/api/music/lists/123/like/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Returns: { "status": "liked", "likes_count": 26 }
// or: { "status": "unliked", "likes_count": 24 }
```

### Get List Likes
**GET** `/api/music/lists/{list_id}/likes/?offset={offset}&limit={limit}`

**Query Parameters:**
- `offset` (optional): Starting position for pagination (default: 0)
- `limit` (optional): Number of results per page (default: 20)

```javascript
const listLikes = await fetch('/api/music/lists/123/likes/?offset=0&limit=20', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Returns:
// {
//   "users": [
//     {
//       "id": 1,
//       "username": "musicfan",
//       "name": "John Smith",
//       "avatar": "https://...",
//       "follower_count": 45,
//       "following_count": 32,
//       "review_count": 28
//     }
//   ],
//   "total_count": 15,
//   "has_more": false,
//   "next_offset": null
// }
```

### Get User's Lists
**GET** `/api/music/users/{username}/lists/`

```javascript
const userLists = await fetch('/api/music/users/musiclover/lists/', {
  headers: { 'Authorization': `Bearer ${authToken}` }
})
.then(res => res.json());

// Returns array of user's lists
// - Shows all lists if viewing own profile
// - Shows only public lists if viewing others
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

## ✅ Staff Verification System

The API includes a staff verification system that displays blue checkmark badges next to verified staff members' usernames throughout the application.

### Staff Status in API Responses

**User Profile Responses** now include an `is_staff` field:
```javascript
// GET /api/accounts/profile/ or /api/accounts/users/{username}/
{
  "id": 1,
  "username": "staffmember",
  "email": "staff@example.com",
  "bio": "Official staff member",
  "is_staff": true,  // ← Staff verification status
  "followers_count": 150,
  "following_count": 75,
  "review_count": 42
}
```

**Review Responses** include `user_is_staff` field:
```javascript
// GET /api/music/reviews/{id}/ or user review lists
{
  "id": 123,
  "username": "staffmember",
  "user_is_staff": true,  // ← Staff status of review author
  "rating": 9,
  "content": "Excellent album with innovative production...",
  "album_title": "OK Computer",
  "album_artist": "Radiohead",
  "likes_count": 25,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Activity Feed Responses** include staff status:
```javascript
// GET /api/music/activity/
{
  "activity_type": "review",
  "username": "staffmember",
  "user_is_staff": true,  // ← Staff status in activity
  "created_at": "2024-01-15T10:30:00Z",
  "review_details": {
    "id": 123,
    "rating": 9,
    "album_title": "OK Computer",
    "user_is_staff": true  // ← Also included in nested review data
  }
}
```

### Frontend Display

Staff verification is automatically displayed throughout the UI:

- **Profile Pages**: Blue checkmark (✓) next to staff usernames
- **Review Pages**: Verification badge next to reviewer name  
- **Activity Feed**: Checkmarks in activity items
- **Comment Sections**: Staff verification in comment headers

### Security Notes

- **Read-only Field**: The `is_staff` field is read-only in all API responses
- **Admin-only Management**: Staff status can only be modified through Django admin interface
- **No Self-Assignment**: Users cannot modify their own staff status via API
- **Secure Implementation**: Staff status is determined server-side and cannot be manipulated by clients

## 📅 Album Year Display

The application displays album release years alongside album information to provide users with additional context when browsing reviews.

### Where Album Years Appear

- **✅ Review Detail Pages**: Shows year next to artist name (`Artist • Year`)
- **✅ Profile Page Reviews**: Displays year in review cards (`Artist • Year`)  
- **❌ Activity Feed**: Year removed to reduce clutter in activity stream

### API Response Format

Album year is included in review responses as `album_year`:

```javascript
// GET /api/music/reviews/{id}/
{
  "id": 123,
  "album_title": "OK Computer",
  "album_artist": "Radiohead", 
  "album_year": 1997,  // ← Album release year
  "rating": 9,
  "content": "A groundbreaking album...",
  "username": "reviewer",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Frontend Display Examples

**Review Detail Page:**
```
OK Computer
Radiohead • 1997
★★★★★★★★★☆ 9/10
```

**Profile Page Review Card:**
```
OK Computer
Radiohead • 1997
"A groundbreaking album that redefined alternative rock..."
```

**Activity Feed (no year):**
```
username reviewed OK Computer by Radiohead and rated it 9/10
```

### Implementation Notes

- **Optional Field**: Year only displays when available (`album_year` can be null)
- **Graceful Fallback**: Missing years don't break the display
- **Consistent Formatting**: Uses bullet separator (•) for clean visual separation
- **Selective Display**: Shown in detailed views but omitted from activity feed for brevity

## 📝 Rich Text Formatting System

The application includes a rich text formatting system for reviews and comments, supporting markdown-style syntax with a visual toolbar.

### Supported Formatting

- **Bold Text**: `**bold text**` or use Bold button (B)
- **Italic Text**: `*italic text*` or use Italic button (I)  
- **Underlined Text**: `__underlined text__` or use Underline button (U)
- **Strikethrough Text**: `~~strikethrough text~~` or use Strikethrough button (S)

### Toolbar Interface

The rich text editor includes a formatting toolbar with buttons for:
- **Bold (B)**: Apply/remove bold formatting
- **Italic (I)**: Apply/remove italic formatting  
- **Underline (U)**: Apply/remove underline formatting
- **Strikethrough (S)**: Apply/remove strikethrough formatting

### Usage in Reviews and Comments

```javascript
// Example formatted review content
const reviewContent = `This album is **absolutely incredible**. The production quality is *outstanding*, and tracks like "__Paranoid Android__" showcase the band's ~~experimental~~ **innovative** approach.`;

// The formatting is automatically rendered in the UI as:
// "This album is absolutely incredible. The production quality is outstanding, 
// and tracks like "Paranoid Android" showcase the band's innovative approach."
```

### Implementation Details

- **Client-side Rendering**: Formatting is applied in real-time as users type
- **Server Storage**: Raw markdown-style text is stored in the database
- **Cross-platform**: Formatting works consistently across all devices
- **Accessibility**: Proper semantic HTML is generated for screen readers

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
            <strong>${activity.username}</strong>
            ${activity.user_is_staff ? '<span style="color: #3b82f6; margin-left: 4px;">✓</span>' : ''}
            reviewed <strong>${review.album_title}</strong> by ${review.album_artist}
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
- **Favorite Albums**: Beautiful grid showcasing up to 5 favorite albums with hover effects and user ratings
- **Pinned Reviews**: Up to 2 highlighted favorite reviews at the top (reduced from 4)
- **Review Grid**: Compact album covers (120px) in Letterboxd-style layout
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

### 👥 Review Likes Pages (`/review/{id}/likes/`)
- **Clean User Display**: Shows users who liked a review in a grid layout
- **User Stats**: Displays follower count, following count, and review count for each user
- **Username Format**: Shows display name and @username for clear identification
- **Profile Links**: Clickable user cards that navigate to user profiles
- **Pagination**: Load more users with smooth scrolling
- **Review Context**: Shows review details at the top (album, artist, reviewer without rating text)
- **Minimalist Design**: Focuses on user statistics instead of bio text for cleaner presentation
- **Responsive Grid**: Adapts to different screen sizes with auto-fill columns
- **Data Available**: While bio and location data are available in the API, the UI shows only stats for better UX

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
| GET | `/api/accounts/favorite-albums/` | Get current user's favorite albums | Yes |
| POST | `/api/accounts/favorite-albums/` | Add album to favorites (max 5) | Yes |
| DELETE | `/api/accounts/favorite-albums/` | Remove album from favorites | Yes |

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
| GET | `/api/music/reviews/{review_id}/likes/` | Get review likes (with optional pagination & review details) | Optional |

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

## 🆕 Recent Updates & New Features

### 📌 Pinned Reviews Limit (Updated)
- **Previous**: Users could pin up to 4 reviews
- **Current**: Users can now pin up to 2 reviews maximum
- **Reasoning**: Cleaner profile layout, more selective curation
- **Error Handling**: Attempting to pin a 3rd review returns: `{"error": "You can only pin up to 2 reviews"}`
- **Cache Optimization**: Pinning/unpinning now triggers immediate cache invalidation for instant UI updates

### ❤️ Favorite Albums (New Feature)
- **Concept**: Similar to Letterboxd's 4 favorite movies, but for albums (max 5)
- **Display**: Beautiful grid layout on user profiles with album covers and user ratings
- **User Experience**: Hover effects, remove buttons, clickable albums linking to reviews
- **API Integration**: Full CRUD operations via `/api/accounts/favorite-albums/`
- **Data Richness**: Shows user's rating and review excerpt if they've reviewed the album
- **Responsive Design**: Adapts to different screen sizes with auto-fill grid layout

### 🚀 Performance Improvements
- **Profile Cache Invalidation**: Pinning/unpinning reviews now properly invalidates profile cache
- **Immediate UI Updates**: Both pinned reviews and favorite albums update instantly without page refresh
- **Error Messages**: More specific error messages for better user experience
- **Database Optimization**: Efficient queries for favorite albums with user review data

### 🎨 UI/UX Enhancements
- **Profile Layout**: Favorite Albums section appears between "Most Reviewed Genres" and "Pinned Reviews"
- **Visual Hierarchy**: Cleaner profile organization with focused content sections
- **Interactive Elements**: Smooth hover animations and intuitive remove functionality
- **Mobile Optimization**: Touch-friendly interactions for favorite albums management

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
- **Staff Verification System**: Blue checkmark badges for verified staff members
- **Rate Limiting**: Protection against API abuse

### 🎵 Music & Reviews
- **Discogs Integration**: Access to comprehensive music database
- **Rich Review System**: Consistent 1-10 ratings with detailed text reviews and intuitive slider UI
- **Rich Text Editor**: Markdown-style formatting with toolbar buttons for enhanced review writing
- **Custom Genre Tagging**: User-assigned genres for personalized organization
- **Review Management**: Edit, delete, pin/unpin reviews with modal interface
- **Social Interactions**: Like reviews with race condition prevention, follow users, comment on reviews
- **Rating Validation**: Automatic clamping to prevent ratings outside 1-10 range

### 💬 Comments & Interactions
- **Threaded Comments**: Full comment system with edit/delete functionality
- **Rich Text Formatting**: Markdown-style formatting with toolbar (Bold, Italic, Underline, Strikethrough)
- **Pagination**: Efficient loading of large comment threads
- **Real-time Updates**: Immediate UI feedback for all interactions
- **Permission-based Actions**: Users can only edit/delete their own content
- **Review Likes Pages**: Dedicated pages showing users who liked reviews with user stats (followers, following, review count)
- **Enhanced User Display**: Clean user cards with @username format and social statistics instead of bio text

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
- **Enhanced User Serializers**: UserSerializer now includes follower_count, following_count, and review_count for comprehensive user statistics
- **PostgreSQL**: Reliable database with proper indexing
- **Modern JavaScript**: ES6+ features, async/await, fetch API
- **CSS Grid & Flexbox**: Modern layout techniques
- **JWT Token Management**: Secure client-side token handling

### 🚀 Performance & Caching
- **Multi-Tier Caching**: Redis Cloud + database cache fallback (90% faster activity feeds)
- **Query Optimization**: 85% reduction in database queries (from 50+ to 3-5 per request)
- **Smart Cache Invalidation**: Maintains data consistency with intelligent cache clearing
- **Profile Cache Invalidation**: Automatic cache refresh when profiles are updated
  - Invalidates user profile cache, activity feeds, and follower feeds
  - Ensures immediate visibility of profile changes across the platform
  - Triggers comprehensive cache refresh for optimal user experience
- **Efficient Pagination**: Offset-based pagination for large datasets
- **Optimized Database Indexes**: Compound indexes for activity feeds and user queries
- **Lazy Loading**: Comments and activity load on demand
- **Serverless Optimized**: Built for Vercel deployment with 60% faster cold starts

📊 **Performance Results**: Activity feed loads in 200-500ms (down from 2-5 seconds)  
📖 **Detailed Documentation**: See [CACHING_STRATEGY.md](./CACHING_STRATEGY.md) for complete implementation details

---

**Built with Django, PostgreSQL, and modern JavaScript. Inspired by Letterboxd's elegant approach to media discovery and social sharing.**

*This platform demonstrates modern web development practices with a focus on user experience, performance, and maintainable code architecture.*
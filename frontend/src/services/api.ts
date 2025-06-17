import axios from 'axios';

// For integrated deployment (frontend and backend served together)
const API_BASE_URL = process.env.REACT_APP_API_URL || (
  process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000'
);

// Create axios instance with base configuration
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired, clear auth data
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface User {
  id: number;
  username: string;
  email?: string;
  name?: string;
  display_name: string;
  bio?: string;
  location?: string;
  avatar?: string;
  follower_count: number;
  following_count: number;
  review_count?: number;
  pinned_reviews?: Review[];
  is_following?: boolean;
  favorite_genres?: Array<{ id: number; name: string }>;
}

export interface Album {
  id: string;
  title: string;
  artist: string;
  year?: number;
  cover_url?: string;
  cover_image?: string;
  genres?: string[];
  discogs_id: number;
}

export interface Review {
  id: number;
  username: string;
  rating: number;
  content: string;
  created_at: string;
  album_title: string;
  album_artist: string;
  album_cover: string;
  album_year?: number;
  is_pinned: boolean;
  likes_count: number;
  is_liked_by_user: boolean;
  comments_count: number;
  user_genres: Array<{ id: number; name: string }>;
}

export interface Comment {
  id: number;
  user: User;
  content: string;
  created_at: string;
}

export interface SearchResult {
  id: string;
  discogs_id?: string;
  title: string;
  artist: string;
  year?: number;
  cover_image?: string;
  thumb?: string;
  genre?: string[];
  style?: string[];
}

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    try {
      const response = await api.post('/api/accounts/login/', { username, password });
      const data = response.data;
      
      // Store tokens properly
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
      }
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token);
      }
      
      return data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Login failed');
    }
  },
  
  register: async (username: string, email: string, password: string) => {
    try {
      const response = await api.post('/api/accounts/register/', { username, email, password });
      const data = response.data;
      
      // Store tokens properly
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
      }
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token);
      }
      
      return data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Registration failed');
    }
  },
  
  getProfile: async () => {
    try {
      const response = await api.get('/api/accounts/profile/');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get profile');
    }
  },
  
  logout: async () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    return { success: true };
  }
};

// Music API
export const musicAPI = {
  search: async (query: string) => {
    try {
      const response = await api.get(`/api/music/search/?q=${encodeURIComponent(query)}`);
      return response.data; // Backend returns {results: [...]}
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Search failed');
    }
  },
  
  getAlbumDetails: async (discogsId: string) => {
    try {
      const response = await api.get(`/api/music/albums/${discogsId}/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get album details');
    }
  },
  
  createReview: async (discogsId: string, rating: number, content: string, genres: string[]) => {
    try {
      const response = await api.post(`/api/music/albums/${discogsId}/review/`, {
        rating,
        content,
        genres
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to create review');
    }
  },
  
  getReview: async (reviewId: number) => {
    try {
      const response = await api.get(`/api/music/reviews/${reviewId}/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get review');
    }
  },
  
  updateReview: async (reviewId: number, rating: number, content: string, genres: string[]) => {
    try {
      const response = await api.put(`/api/music/reviews/${reviewId}/`, {
        rating,
        content,
        genres
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to update review');
    }
  },
  
  deleteReview: async (reviewId: number) => {
    try {
      const response = await api.delete(`/api/music/reviews/${reviewId}/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to delete review');
    }
  },
  
  likeReview: async (reviewId: number) => {
    try {
      const response = await api.post(`/api/music/reviews/${reviewId}/like/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to like review');
    }
  },

  getReviewLikes: async (reviewId: number) => {
    try {
      const response = await api.get(`/api/music/reviews/${reviewId}/likes/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get review likes');
    }
  },
  
  getReviewLikesPage: async (reviewId: number, offset = 0) => {
    try {
      const response = await api.get(`/api/music/reviews/${reviewId}/likes/?offset=${offset}&include_review=true`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get review likes page');
    }
  },
  
  pinReview: async (reviewId: number) => {
    try {
      const response = await api.post(`/api/music/reviews/${reviewId}/pin/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to pin review');
    }
  },
  

  
  getActivityFeed: async (type: 'friends' | 'you' | 'incoming' = 'friends') => {
    try {
      const response = await api.get(`/api/music/activity/?type=${type}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get activity feed');
    }
  },
  
  getComments: async (reviewId: number, offset = 0, limit = 10) => {
    try {
      const response = await api.get(`/api/music/reviews/${reviewId}/comments/?offset=${offset}&limit=${limit}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get comments');
    }
  },
  
  createComment: async (reviewId: number, content: string) => {
    try {
      const response = await api.post(`/api/music/reviews/${reviewId}/comments/`, { content });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to create comment');
    }
  },
  
  updateComment: async (commentId: number, content: string) => {
    try {
      const response = await api.put(`/api/music/comments/${commentId}/`, { content });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to update comment');
    }
  },
  
  deleteComment: async (commentId: number) => {
    try {
      const response = await api.delete(`/api/music/comments/${commentId}/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to delete comment');
    }
  },
  
  deleteActivity: async (activityId: number) => {
    try {
      const response = await api.delete(`/api/music/activity/${activityId}/delete/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to delete activity');
    }
  }
};

// User API
export const userAPI = {
  getProfile: async (username: string) => {
    try {
      const response = await api.get(`/api/accounts/users/${username}/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get user profile');
    }
  },
  
  getUserReviews: async (username: string) => {
    try {
      const response = await api.get(`/api/accounts/users/${username}/reviews/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get user reviews');
    }
  },
  
  updateProfile: async (data: FormData | { bio?: string; name?: string; location?: string; favorite_genres?: string[]; avatar?: File }) => {
    try {
      let formData: FormData;
      
      if (data instanceof FormData) {
        formData = data;
      } else {
        formData = new FormData();
        if (data.bio !== undefined) {
          formData.append('bio', data.bio);
        }
        if (data.name !== undefined) {
          formData.append('name', data.name);
        }
        if (data.location !== undefined) {
          formData.append('location', data.location);
        }
        if (data.favorite_genres !== undefined) {
          formData.append('favorite_genres', JSON.stringify(data.favorite_genres));
        }
        if (data.avatar) {
          formData.append('avatar', data.avatar);
        }
      }
      
      const response = await api.put('/api/accounts/profile/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to update profile');
    }
  },
  
  followUser: async (username: string) => {
    try {
      const response = await api.post(`/api/accounts/users/${username}/follow/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to follow user');
    }
  },
  
  unfollowUser: async (username: string) => {
    try {
      const response = await api.post(`/api/accounts/users/${username}/unfollow/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to unfollow user');
    }
  },
  
  getFollowers: async (username: string) => {
    try {
      const response = await api.get(`/api/accounts/users/${username}/followers/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get followers');
    }
  },
  
  getFollowing: async (username: string) => {
    try {
      const response = await api.get(`/api/accounts/users/${username}/following/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get following');
    }
  },
  
  searchUsers: async (query: string) => {
    try {
      const response = await api.get(`/api/accounts/users/search/?q=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'User search failed');
    }
  },

  async getUserFollowing(username: string): Promise<any> {
    try {
      const response = await api.get(`/api/accounts/users/${username}/following/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get following');
    }
  },

  async getUserGenreStats(username: string): Promise<any> {
    try {
      const response = await api.get(`/api/accounts/users/${username}/genre-stats/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get genre stats');
    }
  },

  getReviewLikes: async (reviewId: number) => {
    try {
      const response = await api.get(`/api/music/reviews/${reviewId}/likes/`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to get review likes');
    }
  }
};

export default api; 
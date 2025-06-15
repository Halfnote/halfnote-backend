import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';
import { userAPI, musicAPI } from '../services/api';
import EditReviewModal from '../components/EditReviewModal';
import { renderFormattedText } from '../utils/textFormatting';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
`;

const BackLink = styled.button`
  background: none;
  border: none;
  color: #6b7280;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;

  &:hover {
    color: #111827;
  }
`;

const ProfileHeader = styled.div`
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: relative;
`;

const ProfileInfo = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 24px;
`;

const ProfileTopRight = styled.div`
  position: absolute;
  top: 32px;
  right: 32px;
  display: flex;
  align-items: center;
  gap: 16px;
`;

const ProfileAllStats = styled.div`
  display: flex;
  gap: 32px;
  margin-bottom: 16px;
  align-items: center;
`;

const ProfileAvatar = styled.img`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s ease;

  &:hover {
    transform: scale(1.05);
  }
`;

const ProfileDetails = styled.div`
  flex: 1;
`;

const ProfileName = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
`;

const ProfileBio = styled.p`
  color: #6b7280;
  font-size: 16px;
  margin-bottom: 16px;
  white-space: pre-wrap;
`;

const ProfileStats = styled.div`
  display: flex;
  gap: 32px;
  margin-bottom: 16px;
  align-items: center;
`;

const Stat = styled.div`
  text-align: center;
  min-width: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const StatLink = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: none;
  color: inherit;
  transition: color 0.2s ease;
  text-align: center;
  min-width: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0;

  &:hover {
    color: #667eea;
  }
`;

const StatNumber = styled.span`
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  line-height: 1.2;
  margin-bottom: 4px;
`;

const StatLabel = styled.span`
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
  line-height: 1;
`;

const FollowButton = styled.button<{ $isFollowing?: boolean }>`
  background: ${props => props.$isFollowing ? 'white' : '#111827'};
  color: ${props => props.$isFollowing ? '#374151' : 'white'};
  border: ${props => props.$isFollowing ? '1px solid #d1d5db' : 'none'};
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.$isFollowing ? '#fee2e2' : '#374151'};
    color: ${props => props.$isFollowing ? '#dc2626' : 'white'};
    border-color: ${props => props.$isFollowing ? '#fca5a5' : 'transparent'};
  }
`;

const EditProfileButton = styled.button`
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;

  &:hover {
    background: #f9fafb;
  }
`;

const GenresList = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
`;

const GenreTag = styled.span`
  background: #f3f4f6;
  color: #374151;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
`;

const TabsContainer = styled.div`
  background: white;
  border-radius: 16px;
  padding: 0;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const TabsList = styled.div`
  display: flex;
  border-bottom: 1px solid #e5e7eb;
`;

const Tab = styled.button<{ $active?: boolean }>`
  background: ${props => props.$active ? '#111827' : 'transparent'};
  color: ${props => props.$active ? 'white' : '#6b7280'};
  border: none;
  padding: 16px 24px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 0;

  &:hover {
    background: ${props => props.$active ? '#111827' : '#f9fafb'};
    color: ${props => props.$active ? 'white' : '#111827'};
  }
`;

const TabContent = styled.div`
  padding: 32px;
`;

const ReviewsSection = styled.div`
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 24px;
`;

const ReviewItem = styled.div`
  display: flex;
  gap: 16px;
  padding: 20px 0;
  border-bottom: 1px solid #f3f4f6;
  position: relative;

  &:last-child {
    border-bottom: none;
  }
`;

const ReviewAlbumCover = styled.img`
  width: 120px;
  height: 120px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
`;

const ReviewContentWrapper = styled.div`
  flex: 1;
`;

const ReviewHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
`;

const ReviewHeaderRight = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ReviewAlbumTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
`;

const ReviewTitleLink = styled.button`
  background: none;
  border: none;
  color: #111827;
  text-decoration: none;
  transition: color 0.2s ease;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  text-align: left;
  padding: 0;

  &:hover {
    color: #667eea;
    text-decoration: underline;
  }
`;

const ReviewAlbumArtist = styled.p`
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
`;

const ReviewRating = styled.span`
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
`;

const ReviewRatingSection = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
`;

const ReviewEngagement = styled.div`
  font-size: 11px;
  color: #9ca3af;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const ReviewBottomActions = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
`;

const ReviewEngagementActions = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 12px;
  color: #6b7280;
`;

const EngagementButton = styled.button<{ $active?: boolean }>`
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  color: ${props => props.$active ? '#ef4444' : '#6b7280'};
  transition: color 0.2s ease;
  padding: 4px;
  border-radius: 4px;
  
  &:hover:not(:disabled) {
    color: ${props => props.$active ? '#dc2626' : '#374151'};
    background: #f9fafb;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ReviewContent = styled.p`
  color: #374151;
  line-height: 1.5;
  margin-bottom: 8px;
`;

const ReviewMeta = styled.div`
  font-size: 12px;
  color: #9ca3af;
`;

const ReviewUserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
`;

const ReviewUserAvatar = styled.img`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
`;

const ReviewUsername = styled.span`
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
`;

const LoadingDiv = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #6b7280;
`;

const Spinner = styled.div`
  width: 40px;
  height: 40px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 16px;
  border-radius: 8px;
  margin: 16px 0;
  text-align: center;
`;

const SuccessMessage = styled.div`
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
  padding: 16px;
  border-radius: 8px;
  margin: 16px 0;
  text-align: center;
`;

const NoReviews = styled.div`
  text-align: center;
  color: #6b7280;
  padding: 40px 20px;
  font-style: italic;
`;

const EditProfileModal = styled.div<{ $visible: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: ${props => props.$visible ? 'flex' : 'none'};
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const ModalTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: #111827;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    color: #111827;
  }
`;

const FormGroup = styled.div`
  margin-bottom: 16px;
`;

const Label = styled.label`
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
`;

const Input = styled.input`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const SaveButton = styled.button`
  background: #111827;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s ease;

  &:hover {
    background: #374151;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const ReviewActions = styled.div`
  display: flex;
  gap: 4px;
  margin-top: 8px;
`;

const ActionButton = styled.button<{ $pinned?: boolean }>`
  background: ${props => props.$pinned ? '#fef3c7' : '#f3f4f6'};
  border: ${props => props.$pinned ? '1px solid #f59e0b' : 'none'};
  color: ${props => props.$pinned ? '#92400e' : '#6b7280'};
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: ${props => props.$pinned ? '#fde68a' : '#e5e7eb'};
    color: #374151;
  }
`;

const LikeButton = styled.button<{ $liked?: boolean }>`
  background: none;
  border: none;
  cursor: pointer;
  color: ${props => props.$liked ? '#dc2626' : '#6b7280'};
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;

  &:hover {
    color: ${props => props.$liked ? '#b91c1c' : '#374151'};
  }
`;

const LikesModal = styled.div<{ $visible: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: ${props => props.$visible ? 'flex' : 'none'};
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const LikesModalContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
  max-height: 500px;
  overflow-y: auto;
`;

const LikesModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
`;

const LikesModalTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0;
`;

const LikeUserItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;

  &:last-child {
    border-bottom: none;
  }
`;

const LikeUserAvatar = styled.img`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
`;

const LikeUserName = styled.span`
  font-weight: 500;
  color: #111827;
`;

const GenreGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
`;

const GenreOption = styled.label`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s ease;

  &:hover {
    background: #f3f4f6;
  }

  input[type="checkbox"] {
    margin: 0;
  }
`;

const AvatarPreview = styled.img`
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  margin: 20px auto 0;
  border: 3px solid #e5e7eb;
  display: block;
`;

interface User {
  id: number;
  username: string;
  name?: string;
  display_name: string;
  bio?: string;
  location?: string;
  avatar?: string;
  follower_count: number;
  following_count: number;
  review_count: number;
  favorite_genres: Array<{ id: number; name: string }>;
  is_following?: boolean;
  is_staff?: boolean;
}

interface Review {
  id: number;
  username: string;
  user_avatar?: string;
  album_title: string;
  album_artist: string;
  album_cover?: string;
  rating: number;
  content: string;
  created_at: string;
  is_pinned: boolean;
  likes_count: number;
  comments_count: number;
  is_liked_by_user: boolean;
}

const ProfilePage: React.FC = () => {
  const { username } = useParams<{ username: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [profileUser, setProfileUser] = useState<User | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'reviews'>('reviews');
  
  // Edit profile modal state
  const [showEditModal, setShowEditModal] = useState(false);
  const [editBio, setEditBio] = useState('');
  const [editName, setEditName] = useState('');
  const [editLocation, setEditLocation] = useState('');
  const [editFavoriteGenres, setEditFavoriteGenres] = useState<string[]>([]);
  const [editAvatar, setEditAvatar] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string>('');
  const [availableGenres, setAvailableGenres] = useState<Array<{ id: number; name: string }>>([]);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState<string>('');
  const [profileError, setProfileError] = useState<string>('');
  
  // Likes modal state
  const [showLikesModal, setShowLikesModal] = useState(false);
  const [likesData, setLikesData] = useState<{ users: Array<{ id: number; username: string; avatar?: string }> } | null>(null);
  const [loadingLikes, setLoadingLikes] = useState(false);
  
  // Edit review modal state
  const [showEditReviewModal, setShowEditReviewModal] = useState(false);
  const [editingReviewId, setEditingReviewId] = useState<number | null>(null);
  const [likingReviews, setLikingReviews] = useState<Set<number>>(new Set()); // Track which reviews are being liked

  const isOwnProfile = user?.username === username;
  const pinnedReviews = reviews.filter(review => review.is_pinned);

  const loadProfile = useCallback(async () => {
    if (!username) return;
    
    try {
      const userData = await userAPI.getProfile(username);
      setProfileUser(userData);
      
      // Initialize edit form with current data
      if (isOwnProfile) {
        setEditBio(userData.bio || '');
        setEditName(userData.name || '');
        setEditLocation(userData.location || '');
        setEditFavoriteGenres(
          userData.favorite_genres?.map((g: any) => 
            typeof g === 'string' ? g : g.name
          ) || []
        );
        setAvatarPreview(userData.avatar || '');
      }
    } catch (err: any) {
      console.error('Failed to load profile:', err);
      throw err; // Re-throw to be caught by loadData
    }
  }, [username, isOwnProfile]);

  const loadReviews = useCallback(async () => {
    if (!username) return;
    
    try {
      const reviewsData = await userAPI.getUserReviews(username);
      // Sort reviews by creation date (newest first - LIFO)
      const sortedReviews = reviewsData.sort((a: Review, b: Review) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setReviews(sortedReviews);
    } catch (err: any) {
      console.error('Failed to load reviews:', err);
    }
  }, [username]);

  const loadData = useCallback(async () => {
    if (!username) return;
    
    setLoading(true);
    setError('');
    setProfileUser(null);
    
    try {
      // Load both profile and reviews in parallel
      await Promise.all([
        loadProfile(),
        loadReviews()
      ]);
    } catch (err: any) {
      console.error('Failed to load data:', err);
      setError(err.message || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  }, [username, loadProfile, loadReviews]);

  const loadGenres = useCallback(async () => {
    try {
      const genresData = await musicAPI.getGenres();
      setAvailableGenres(genresData.genres || []);
    } catch (error) {
      console.error('Error loading genres:', error);
    }
  }, []);

  const handleFollow = async () => {
    if (!profileUser || !user) return;
    
    try {
      if (profileUser.is_following) {
        await userAPI.unfollowUser(profileUser.username);
        setProfileUser({
          ...profileUser,
          is_following: false,
          follower_count: profileUser.follower_count - 1
        });
      } else {
        await userAPI.followUser(profileUser.username);
        setProfileUser({
          ...profileUser,
          is_following: true,
          follower_count: profileUser.follower_count + 1
        });
      }
    } catch (error) {
      console.error('Error following/unfollowing user:', error);
    }
  };

  const handleEditProfile = () => {
    loadGenres();
    setSuccess('');
    setProfileError('');
    setShowEditModal(true);
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setEditAvatar(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setAvatarPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleGenreToggle = (genreName: string) => {
    setEditFavoriteGenres(prev => 
      prev.includes(genreName)
        ? prev.filter(g => g !== genreName)
        : [...prev, genreName]
    );
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    
    try {
      const formData = new FormData();
      
      formData.append('bio', editBio.trim());
      formData.append('name', editName.trim());
      formData.append('location', editLocation.trim());
      formData.append('favorite_genres', JSON.stringify(editFavoriteGenres));
      
      if (editAvatar) {
        formData.append('avatar', editAvatar);
      }

      const updatedUser = await userAPI.updateProfile(formData);
      
      // Update the profile user state immediately with the response data
      setProfileUser(updatedUser);
      
      // Update avatar preview if a new avatar was uploaded
      if (editAvatar && updatedUser.avatar) {
        setAvatarPreview(updatedUser.avatar);
      }
      
      // Clear the edit avatar file since it's now saved
      setEditAvatar(null);
      
      setShowEditModal(false);
      
      // Reload the profile data to ensure everything is fresh and consistent
      await loadProfile();
      
      // Modern UX: Show success without requiring user action
      setSuccess('Profile updated successfully!');
      setTimeout(() => setSuccess(''), 3000); // Auto-hide after 3 seconds
    } catch (error: any) {
      console.error('Error updating profile:', error);
      setProfileError('Failed to update profile: ' + (error.response?.data?.error || error.message || 'Unknown error'));
      setTimeout(() => setProfileError(''), 5000); // Auto-hide error after 5 seconds
    } finally {
      setSaving(false);
    }
  };

  const getTimeAgo = (dateString: string) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      const days = Math.floor(diff / 86400000);
      const hours = Math.floor(diff / 3600000);
      const minutes = Math.floor(diff / 60000);

      if (days > 0) return `${days}d ago`;
      if (hours > 0) return `${hours}h ago`;
      return `${minutes}m ago`;
    } catch (error) {
      return 'Unknown time';
    }
  };

  const handlePinReview = async (reviewId: number, currentlyPinned: boolean) => {
    if (!user || !isOwnProfile) return;
    
    try {
      await musicAPI.pinReview(reviewId);
      
      // Reload reviews to get updated pin status
      loadReviews();
    } catch (error: any) {
      console.error('Error toggling pin:', error);
      alert('Error updating pin status');
    }
  };

  const handleEditReview = (reviewId: number) => {
    setEditingReviewId(reviewId);
    setShowEditReviewModal(true);
  };

  const handleCloseEditReviewModal = () => {
    setShowEditReviewModal(false);
    setEditingReviewId(null);
  };

  const handleSaveEditReview = () => {
    // Reload reviews to show the updated review
    loadReviews();
    loadProfile(); // Also reload profile to update review count if needed
  };

  const handleDeleteReview = async (reviewId: number) => {
    if (!user || !isOwnProfile) return;
    
    if (!window.confirm('Are you sure you want to delete this review?')) return;
    
    try {
      await musicAPI.deleteReview(reviewId);
      
      // Reload reviews to remove deleted review
      loadReviews();
      loadProfile(); // Update review count
    } catch (error: any) {
      console.error('Error deleting review:', error);
      alert('Error deleting review');
    }
  };

  const handleLikeReview = async (reviewId: number, currentlyLiked: boolean) => {
    if (!user || likingReviews.has(reviewId)) return; // Prevent double-clicks
    
    setLikingReviews(prev => new Set(prev).add(reviewId));
    try {
      await musicAPI.likeReview(reviewId);
      
      // Update the review in both pinned and regular reviews
      const updateReview = (review: Review) => {
        if (review.id === reviewId) {
          return {
            ...review,
            is_liked_by_user: !currentlyLiked,
            likes_count: currentlyLiked ? review.likes_count - 1 : review.likes_count + 1
          };
        }
        return review;
      };
      
      setReviews(prev => prev.map(updateReview));
    } catch (error: any) {
      console.error('Error toggling like:', error);
      alert('Error updating like status');
    } finally {
      setLikingReviews(prev => {
        const newSet = new Set(prev);
        newSet.delete(reviewId);
        return newSet;
      });
    }
  };

  const handleShowLikes = async (reviewId: number) => {
    setLoadingLikes(true);
    setShowLikesModal(true);
    
    try {
      const data = await musicAPI.getReviewLikes(reviewId);
      setLikesData(data);
    } catch (error: any) {
      console.error('Error loading likes:', error);
      alert('Error loading likes');
      setShowLikesModal(false);
    } finally {
      setLoadingLikes(false);
    }
  };

  const renderReview = (review: Review) => (
    <ReviewItem key={review.id}>
      <ReviewAlbumCover 
        src={review.album_cover || '/static/music/default-album.svg'} 
        alt={review.album_title}
        onClick={() => navigate(`/review/${review.id}/`)}
        onError={(e) => {
          (e.target as HTMLImageElement).src = '/static/music/default-album.svg';
        }}
      />
      <ReviewContentWrapper>
        <ReviewHeader>
          <div>
            <ReviewAlbumTitle>
              <ReviewTitleLink onClick={() => navigate(`/review/${review.id}/`)}>
                {review.album_title}
                {review.is_pinned && ' 📌'}
              </ReviewTitleLink>
            </ReviewAlbumTitle>
            <ReviewAlbumArtist>{review.album_artist}</ReviewAlbumArtist>
          </div>
          <ReviewHeaderRight>
            <ReviewRatingSection>
              <ReviewRating>{review.rating}/10</ReviewRating>
              <ReviewEngagement>
                <span>{review.likes_count} likes</span>
                <span>{review.comments_count} comments</span>
              </ReviewEngagement>
            </ReviewRatingSection>
          </ReviewHeaderRight>
        </ReviewHeader>
        <ReviewContent>
          {renderFormattedText(review.content)}
        </ReviewContent>
        <ReviewBottomActions>
          <ReviewMeta>
            {getTimeAgo(review.created_at)}
          </ReviewMeta>
          <ReviewEngagementActions>
            <EngagementButton 
              $active={review.is_liked_by_user}
              onClick={() => handleLikeReview(review.id, review.is_liked_by_user)}
              disabled={likingReviews.has(review.id)}
              title={review.is_liked_by_user ? 'Unlike' : 'Like'}
            >
              {likingReviews.has(review.id) ? '⏳' : '❤️'} {review.likes_count}
            </EngagementButton>
            <EngagementButton 
              onClick={() => navigate(`/review/${review.id}/`)}
              title="View comments"
            >
              💬 {review.comments_count}
            </EngagementButton>
          </ReviewEngagementActions>
        </ReviewBottomActions>
        
        {/* Show action buttons for own profile */}
        {isOwnProfile && (
          <ReviewActions>
            <ActionButton 
              onClick={() => handleEditReview(review.id)}
              title="Edit Review"
            >
              ✏️
            </ActionButton>
            <ActionButton 
              $pinned={review.is_pinned}
              onClick={() => handlePinReview(review.id, review.is_pinned)}
              title={review.is_pinned ? 'Unpin Review' : 'Pin Review'}
            >
              {review.is_pinned ? '📌' : '📍'}
            </ActionButton>
            <ActionButton 
              onClick={() => handleDeleteReview(review.id)}
              title="Delete Review"
            >
              🗑️
            </ActionButton>
          </ReviewActions>
        )}
      </ReviewContentWrapper>
    </ReviewItem>
  );

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return (
      <Container>
        <LoadingDiv>
          <Spinner />
          <p>Loading profile...</p>
        </LoadingDiv>
      </Container>
    );
  }

  if (error || (!loading && !profileUser)) {
    return (
      <Container>
        <BackLink onClick={() => navigate(-1)}>
          ← Back to Home
        </BackLink>
        <ErrorMessage>
          {error || 'User not found'}
        </ErrorMessage>
      </Container>
    );
  }

  if (!profileUser) {
    return (
      <Container>
        <LoadingDiv>
          <Spinner />
          <p>Loading profile...</p>
        </LoadingDiv>
      </Container>
    );
  }

  return (
    <Container>
      <BackLink onClick={() => navigate(-1)}>
        ← Back to Home
      </BackLink>
      
      <ProfileHeader>
        <ProfileInfo>
          <ProfileAvatar 
            src={profileUser.avatar || '/static/accounts/default-avatar.svg'} 
            alt={profileUser.username}
            onClick={isOwnProfile ? handleEditProfile : undefined}
            onError={(e) => {
              (e.target as HTMLImageElement).src = '/static/accounts/default-avatar.svg';
            }}
            style={{ cursor: isOwnProfile ? 'pointer' : 'default' }}
          />
          <ProfileDetails>
            <ProfileName>
              {profileUser.display_name}
              {profileUser.is_staff && (
                <span 
                  style={{ 
                    marginLeft: '8px', 
                    fontSize: '24px',
                    color: '#3b82f6',
                    fontWeight: 'bold'
                  }}
                  title="Verified Staff"
                >
                  ✓
                </span>
              )}
            </ProfileName>
            <ProfileBio>@{profileUser.username}</ProfileBio>
            {profileUser.location && <ProfileBio>📍 {profileUser.location}</ProfileBio>}
            {profileUser.bio && <ProfileBio>{profileUser.bio}</ProfileBio>}
            {profileUser.favorite_genres && profileUser.favorite_genres.length > 0 && (
              <GenresList>
                {profileUser.favorite_genres.map(genre => (
                  <GenreTag key={genre.id}>{genre.name}</GenreTag>
                ))}
              </GenresList>
            )}
          </ProfileDetails>
        </ProfileInfo>
        
        <ProfileTopRight>
          <ProfileStats>
            <Stat>
              <StatNumber>{profileUser.review_count}</StatNumber>
              <StatLabel>Reviews</StatLabel>
            </Stat>
            <Stat>
              <StatLink onClick={() => navigate(`/users/${profileUser.username}/followers`)}>
                <StatNumber>{profileUser.follower_count}</StatNumber>
                <StatLabel>Followers</StatLabel>
              </StatLink>
            </Stat>
            <Stat>
              <StatLink onClick={() => navigate(`/users/${profileUser.username}/following`)}>
                <StatNumber>{profileUser.following_count}</StatNumber>
                <StatLabel>Following</StatLabel>
              </StatLink>
            </Stat>
          </ProfileStats>
          {isOwnProfile ? (
            <EditProfileButton onClick={handleEditProfile}>
              Edit Profile
            </EditProfileButton>
          ) : user && (
            <FollowButton 
              $isFollowing={profileUser.is_following}
              onClick={handleFollow}
            >
              {profileUser.is_following ? 'Unfollow' : 'Follow'}
            </FollowButton>
          )}
        </ProfileTopRight>
      </ProfileHeader>

      <TabsContainer>
        <TabsList>
          <Tab 
            $active={activeTab === 'reviews'} 
            onClick={() => setActiveTab('reviews')}
          >
            Reviews ({profileUser.review_count})
          </Tab>
        </TabsList>
        
        <TabContent>
          {activeTab === 'reviews' && (
            <>
              {/* Pinned Reviews Section */}
              {pinnedReviews.length > 0 && (
                <ReviewsSection>
                  <SectionTitle>Pinned Reviews</SectionTitle>
                  {pinnedReviews.map(renderReview)}
                </ReviewsSection>
              )}
              
              {/* All Reviews Section */}
              <ReviewsSection>
                <SectionTitle>All Reviews</SectionTitle>
                {reviews.length === 0 ? (
                  <NoReviews>No reviews yet.</NoReviews>
                ) : (
                  reviews.map(renderReview)
                )}
              </ReviewsSection>
            </>
          )}
        </TabContent>
      </TabsContainer>

      {/* Edit Profile Modal */}
      <EditProfileModal $visible={showEditModal}>
        <ModalContent>
          <ModalHeader>
            <ModalTitle>Edit Profile</ModalTitle>
            <CloseButton onClick={() => setShowEditModal(false)}>×</CloseButton>
          </ModalHeader>
          
          {success && (
            <SuccessMessage>
              {success}
            </SuccessMessage>
          )}
          
          {profileError && (
            <ErrorMessage>
              {profileError}
            </ErrorMessage>
          )}
          
          <FormGroup>
            <Label>Name</Label>
            <Input
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              placeholder="Enter your name"
            />
          </FormGroup>
          
          <FormGroup>
            <Label>Location</Label>
            <Input
              value={editLocation}
              onChange={(e) => setEditLocation(e.target.value)}
              placeholder="Enter your location"
            />
          </FormGroup>
          
          <FormGroup>
            <Label>Bio</Label>
            <Textarea
              value={editBio}
              onChange={(e) => setEditBio(e.target.value)}
              placeholder="Tell us about yourself..."
              maxLength={500}
            />
          </FormGroup>
          
                               <FormGroup>
            <Label>Favorite Genres</Label>
            <GenreGrid>
              {availableGenres.map(genre => (
                <GenreOption key={genre.id}>
                  <input
                    type="checkbox"
                    checked={editFavoriteGenres.includes(genre.name)}
                    onChange={() => handleGenreToggle(genre.name)}
                  />
                  {genre.name}
                </GenreOption>
              ))}
            </GenreGrid>
          </FormGroup>
          
          <FormGroup>
            <Label>Avatar</Label>
            <Input
              type="file"
              accept="image/*"
              onChange={handleAvatarChange}
            />
          </FormGroup>
         
          <SaveButton 
            onClick={handleSaveProfile}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </SaveButton>
          
          {avatarPreview && (
            <AvatarPreview
              src={avatarPreview}
              alt="Avatar Preview"
            />
          )}
        </ModalContent>
      </EditProfileModal>

      {/* Likes Modal */}
      <LikesModal $visible={showLikesModal} onClick={() => setShowLikesModal(false)}>
        <LikesModalContent onClick={(e) => e.stopPropagation()}>
          <LikesModalHeader>
            <LikesModalTitle>Likes</LikesModalTitle>
            <CloseButton onClick={() => setShowLikesModal(false)}>×</CloseButton>
          </LikesModalHeader>
          
          {loadingLikes ? (
            <div>Loading...</div>
          ) : likesData && likesData.users.length > 0 ? (
            likesData.users.map(user => (
              <LikeUserItem key={user.id}>
                <LikeUserAvatar 
                  src={user.avatar || '/static/accounts/default-avatar.svg'}
                  alt={user.username}
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/static/accounts/default-avatar.svg';
                  }}
                />
                <LikeUserName>{user.username}</LikeUserName>
              </LikeUserItem>
            ))
          ) : (
            <div>No likes yet.</div>
          )}
        </LikesModalContent>
      </LikesModal>

      {/* Edit Review Modal */}
      <EditReviewModal
        isVisible={showEditReviewModal}
        reviewId={editingReviewId}
        onClose={handleCloseEditReviewModal}
        onSave={handleSaveEditReview}
      />
    </Container>
  );
};

export default ProfilePage; 
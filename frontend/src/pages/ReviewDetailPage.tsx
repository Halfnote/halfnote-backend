import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';
import { musicAPI, userAPI } from '../services/api';
import EditReviewModal from '../components/EditReviewModal';
import FormattedTextEditor from '../components/FormattedTextEditor';
import ArtistPhoto from '../components/ArtistPhoto';
import { renderFormattedText } from '../utils/textFormatting';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
`;

const BackLink = styled.button`
  background: none;
  border: none;
  color: #667eea;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    text-decoration: underline;
  }
`;

const ReviewHeader = styled.div`
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 30px;
  margin-bottom: 30px;
  align-items: start;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
`;

const AlbumCoverContainer = styled.div`
  position: relative;
  width: 250px;
`;

const AlbumCover = styled.img`
  width: 250px;
  height: 250px;
  border-radius: 8px;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);

  @media (max-width: 768px) {
    width: 200px;
    height: 200px;
    margin: 0 auto;
    display: block;
  }
`;

const AlbumMeta = styled.div`
  margin-top: 16px;
  font-size: 14px;
  color: #666;
  display: flex;
  flex-direction: column;
  gap: 8px;

  @media (max-width: 768px) {
    text-align: center;
  }
`;

const UserLikeLine = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;

  @media (max-width: 768px) {
    justify-content: center;
  }
`;

const ReviewerInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #667eea;

  &:hover {
    text-decoration: underline;
  }
`;

const ReviewerAvatar = styled.img`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
`;

const PipeSeparator = styled.span`
  color: #666;
  margin: 0 4px;
`;

const LikeCount = styled.button`
  background: none;
  border: none;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  padding: 0;
  
  &:hover {
    color: #374151;
    text-decoration: underline;
  }
`;

const ReviewInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const TitleRatingRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 16px;
`;

const AlbumTitle = styled.h1`
  font-size: 32px;
  font-weight: 700;
  margin: 0;
  color: #111;
  flex: 1;

  @media (max-width: 768px) {
    font-size: 24px;
  }
`;

const RatingContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 4px;
  margin-right: 8px;
`;

const ActionButton = styled.button<{ $variant?: 'pin' | 'edit' | 'delete' }>`
  background: ${props => {
    if (props.$variant === 'pin') return '#fef3c7';
    if (props.$variant === 'edit') return '#e0f2fe';
    if (props.$variant === 'delete') return '#fee2e2';
    return 'transparent';
  }};
  border: 1px solid ${props => {
    if (props.$variant === 'pin') return '#f59e0b';
    if (props.$variant === 'edit') return '#0284c7';
    if (props.$variant === 'delete') return '#dc2626';
    return '#d1d5db';
  }};
  color: ${props => {
    if (props.$variant === 'pin') return '#92400e';
    if (props.$variant === 'edit') return '#0c4a6e';
    if (props.$variant === 'delete') return '#991b1b';
    return '#666';
  }};
  font-size: 14px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;

  &:hover {
    opacity: 0.8;
    transform: translateY(-1px);
  }
`;

const LikeButton = styled.button<{ $liked?: boolean }>`
  background: ${props => props.$liked ? '#fee2e2' : 'transparent'};
  border: 1px solid ${props => props.$liked ? '#dc2626' : '#d1d5db'};
  color: ${props => props.$liked ? '#dc2626' : '#666'};
  font-size: 16px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  margin-right: 8px;

  &:hover:not(:disabled) {
    opacity: 0.8;
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const FavoriteButton = styled.button<{ $favorited?: boolean }>`
  background: ${props => props.$favorited ? '#fef3c7' : 'transparent'};
  border: 1px solid ${props => props.$favorited ? '#f59e0b' : '#d1d5db'};
  color: ${props => props.$favorited ? '#92400e' : '#666'};
  font-size: 16px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  margin-right: 8px;

  &:hover:not(:disabled) {
    opacity: 0.8;
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const Rating = styled.div`
  background: #111827;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
`;

const ArtistName = styled.p`
  font-size: 20px;
  color: #666;
  margin: 0;

  @media (max-width: 768px) {
    font-size: 16px;
  }
`;

const ArtistSection = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  
  @media (max-width: 768px) {
    justify-content: center;
  }
`;

const Genres = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
`;

const GenreTag = styled.span`
  background: #f3f4f6;
  color: #374151;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
`;

const ReviewContent = styled.div`
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  margin-bottom: 32px;
  line-height: 1.6;
  color: #374151;
  font-size: 16px;

  p {
    margin-bottom: 16px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
`;

const CommentsSection = styled.div`
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
`;

const CommentsHeader = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  margin: 0;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
`;

const CommentForm = styled.div`
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  gap: 12px;
`;

const CommentInput = styled.textarea`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
  outline: none;

  &:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  &::placeholder {
    color: #9ca3af;
  }
`;

const CommentSubmit = styled.button`
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  align-self: flex-end;
  transition: background 0.2s ease;

  &:hover {
    background: #5a67d8;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const CommentsList = styled.div`
  padding: 20px 24px;
`;

const CommentItem = styled.div`
  padding: 16px 0;
  border-bottom: 1px solid #f3f4f6;

  &:last-child {
    border-bottom: none;
  }
`;

const CommentHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

const CommentUsername = styled.span`
  font-weight: 600;
  color: #667eea;
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
`;

const CommentTime = styled.span`
  font-size: 12px;
  color: #9ca3af;
`;

const CommentContent = styled.div`
  color: #374151;
  line-height: 1.5;
`;

const CommentActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 8px;
`;

const CommentActionButton = styled.button`
  background: none;
  border: none;
  color: #6b7280;
  font-size: 12px;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  transition: all 0.2s ease;

  &:hover {
    background: #f3f4f6;
    color: #374151;
  }
`;

const CommentEditForm = styled.div`
  margin-top: 8px;
`;

const CommentEditInput = styled.textarea`
  width: 100%;
  min-height: 60px;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const CommentEditActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 8px;
`;

const CommentEditButton = styled.button<{ $variant?: 'save' | 'cancel' }>`
  background: ${props => props.$variant === 'save' ? '#667eea' : 'transparent'};
  color: ${props => props.$variant === 'save' ? 'white' : '#6b7280'};
  border: 1px solid ${props => props.$variant === 'save' ? '#667eea' : '#d1d5db'};
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.$variant === 'save' ? '#5a67d8' : '#f3f4f6'};
    border-color: ${props => props.$variant === 'save' ? '#5a67d8' : '#9ca3af'};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
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

const EmptyComments = styled.div`
  text-align: center;
  color: #6b7280;
  padding: 40px 20px;
  font-style: italic;
`;

interface Review {
  id: number;
  username: string;
  user_avatar?: string;
  user_is_staff?: boolean;
  album_title: string;
  album_artist: string;
  album_cover?: string;
  album_artist_photo?: string;
  album_year?: number;
  album_discogs_id?: string;
  rating: number;
  content: string;
  created_at: string;
  is_pinned: boolean;
  likes_count: number;
  is_liked_by_user: boolean;
  comments_count: number;
  user_genres: Array<{ id: number; name: string }>;
}

interface Comment {
  id: number;
  username: string;
  user_avatar?: string;
  user_is_staff?: boolean;
  content: string;
  created_at: string;
}

const ReviewDetailPage: React.FC = () => {
  const { reviewId } = useParams<{ reviewId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [review, setReview] = useState<Review | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newComment, setNewComment] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);
  const [editingCommentId, setEditingCommentId] = useState<number | null>(null);
  const [editingCommentContent, setEditingCommentContent] = useState('');
  const [likingReview, setLikingReview] = useState(false); // Add loading state for likes
  const [userFavorites, setUserFavorites] = useState<string[]>([]);
  const [favoriteLoading, setFavoriteLoading] = useState(false);
  
  // Edit review modal state
  const [showEditReviewModal, setShowEditReviewModal] = useState(false);

  const loadReview = useCallback(async () => {
    if (!reviewId) return;
    
    try {
      const data = await musicAPI.getReview(parseInt(reviewId));
      setReview(data);
      setError('');
    } catch (error: any) {
      console.error('Error loading review:', error);
      setError(error.message || 'Failed to load review');
    }
  }, [reviewId]);

  const loadComments = useCallback(async () => {
    if (!reviewId) return;
    
    try {
      const data = await musicAPI.getComments(parseInt(reviewId));
      setComments(Array.isArray(data.comments) ? data.comments : []);
    } catch (error: any) {
      console.error('Error loading comments:', error);
    }
  }, [reviewId]);

  const loadUserFavorites = useCallback(async () => {
    if (!user) return;
    
    try {
      const response = await userAPI.getFavoriteAlbums();
      const favorites = response.favorite_albums || [];
      setUserFavorites(favorites.map((album: any) => album.discogs_id).filter(Boolean));
    } catch (error: any) {
      console.error('Error loading user favorites:', error);
    }
  }, [user]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError('');
    
    await Promise.all([
      loadReview(),
      loadComments(),
      loadUserFavorites()
    ]);
    
    setLoading(false);
  }, [loadReview, loadComments, loadUserFavorites]);

  const toggleLike = async () => {
    if (!review || !user || likingReview) return; // Prevent double-clicks
    
    setLikingReview(true);
    try {
      await musicAPI.likeReview(review.id);
      setReview(prev => prev ? {
        ...prev,
        is_liked_by_user: !prev.is_liked_by_user,
        likes_count: prev.is_liked_by_user ? prev.likes_count - 1 : prev.likes_count + 1
      } : null);
    } catch (error: any) {
      console.error('Error toggling like:', error);
    } finally {
      setLikingReview(false);
    }
  };

  const togglePin = async () => {
    if (!review || !user || review.username !== user.username) return;
    
    try {
      await musicAPI.pinReview(review.id);
      setReview(prev => prev ? {
        ...prev,
        is_pinned: !prev.is_pinned
      } : null);
    } catch (error: any) {
      console.error('Error toggling pin:', error);
    }
  };

  const toggleFavorite = async () => {
    if (!review || !user || !review.album_discogs_id || favoriteLoading) return;

    setFavoriteLoading(true);
    try {
      const isFavorite = userFavorites.includes(review.album_discogs_id);
      
      if (isFavorite) {
        // Remove from favorites
        await userAPI.removeFavoriteAlbum(undefined, review.album_discogs_id);
        setUserFavorites(prev => prev.filter(id => id !== review.album_discogs_id));
      } else {
        // Add to favorites
        await userAPI.addFavoriteAlbum(undefined, review.album_discogs_id);
        setUserFavorites(prev => [...prev, review.album_discogs_id!]);
      }
    } catch (error: any) {
      console.error('Error toggling favorite:', error);
    } finally {
      setFavoriteLoading(false);
    }
  };

  const handleEdit = () => {
    if (!review) return;
    setShowEditReviewModal(true);
  };

  const handleCloseEditReviewModal = () => {
    setShowEditReviewModal(false);
  };

  const handleSaveEditReview = () => {
    // Reload review data to show the updated review
    loadReview();
  };

  const handleDelete = async () => {
    if (!review || !user || review.username !== user.username) return;
    
    if (window.confirm('Are you sure you want to delete this review? This action cannot be undone.')) {
      try {
        await musicAPI.deleteReview(review.id);
        navigate(`/users/${user.username}`);
      } catch (error: any) {
        console.error('Error deleting review:', error);
        alert('Failed to delete review. Please try again.');
      }
    }
  };

  const submitComment = async () => {
    if (!review || !user || !newComment.trim() || submittingComment) return;
    
    setSubmittingComment(true);
    try {
      const comment = await musicAPI.createComment(review.id, newComment.trim());
      setComments(prev => [...prev, comment]);
      setNewComment('');
      setReview(prev => prev ? { ...prev, comments_count: prev.comments_count + 1 } : null);
    } catch (error: any) {
      console.error('Error submitting comment:', error);
    } finally {
      setSubmittingComment(false);
    }
  };

  const startEditComment = (comment: Comment) => {
    setEditingCommentId(comment.id);
    setEditingCommentContent(comment.content);
  };

  const cancelEditComment = () => {
    setEditingCommentId(null);
    setEditingCommentContent('');
  };

  const saveEditComment = async (commentId: number) => {
    if (!editingCommentContent.trim()) return;
    
    try {
      const updatedComment = await musicAPI.updateComment(commentId, editingCommentContent.trim());
      setComments(prev => prev.map(comment => 
        comment.id === commentId ? updatedComment : comment
      ));
      setEditingCommentId(null);
      setEditingCommentContent('');
    } catch (error: any) {
      console.error('Error updating comment:', error);
      alert('Failed to update comment');
    }
  };

  const deleteComment = async (commentId: number) => {
    if (!window.confirm('Are you sure you want to delete this comment?')) return;
    
    try {
      await musicAPI.deleteComment(commentId);
      setComments(prev => prev.filter(comment => comment.id !== commentId));
      setReview(prev => prev ? { ...prev, comments_count: prev.comments_count - 1 } : null);
    } catch (error: any) {
      console.error('Error deleting comment:', error);
      alert('Failed to delete comment');
    }
  };

  const getTimeAgo = (dateString: string) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(diff / 3600000);
      const days = Math.floor(diff / 86400000);

      if (minutes < 60) return `${minutes}m ago`;
      if (hours < 24) return `${hours}h ago`;
      return `${days}d ago`;
    } catch (error) {
      return 'Unknown time';
    }
  };

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return (
      <Container>
        <LoadingDiv>
          <Spinner />
          <p>Loading review...</p>
        </LoadingDiv>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <BackLink onClick={() => navigate(-1)}>
          ← Back to profile
        </BackLink>
        <ErrorMessage>
          {error}
        </ErrorMessage>
      </Container>
    );
  }

  if (!review) {
    return (
      <Container>
        <BackLink onClick={() => navigate(-1)}>
          ← Back to profile
        </BackLink>
        <ErrorMessage>
          Review not found
        </ErrorMessage>
      </Container>
    );
  }

  return (
    <Container>
      <BackLink onClick={() => navigate(-1)}>
        ← Back to profile
      </BackLink>
      
      <ReviewHeader>
        <AlbumCoverContainer>
          <AlbumCover 
            src={review!.album_cover || '/static/music/default-album.svg'} 
            alt={review!.album_title}
            onClick={() => review!.album_discogs_id && navigate(`/albums/${review!.album_discogs_id}/`)}
            style={{ cursor: review!.album_discogs_id ? 'pointer' : 'default' }}
            title={review!.album_discogs_id ? 'View album details' : ''}
            onError={(e) => {
              (e.target as HTMLImageElement).src = '/static/music/default-album.svg';
            }}
          />
        </AlbumCoverContainer>
        
        <ReviewInfo>
          <TitleRatingRow>
            <AlbumTitle 
              onClick={() => review!.album_discogs_id && navigate(`/albums/${review!.album_discogs_id}/`)}
              style={{ 
                cursor: review!.album_discogs_id ? 'pointer' : 'default',
                color: review!.album_discogs_id ? '#667eea' : 'inherit'
              }}
              title={review!.album_discogs_id ? 'View album details' : ''}
            >
              {review!.album_title}
            </AlbumTitle>
            <RatingContainer>
              {user && (
                <LikeButton 
                  $liked={review!.is_liked_by_user}
                  onClick={toggleLike}
                  disabled={likingReview}
                  title="Like"
                >
                  {likingReview ? '⏳' : (review!.is_liked_by_user ? '❤️' : '🤍')}
                </LikeButton>
              )}
              {user && review!.album_discogs_id && (
                <FavoriteButton 
                  $favorited={userFavorites.includes(review!.album_discogs_id)}
                  onClick={toggleFavorite}
                  disabled={favoriteLoading}
                  title={userFavorites.includes(review!.album_discogs_id) ? 'Remove from Favorites' : 'Add to Favorites'}
                >
                  {favoriteLoading ? '⏳' : (userFavorites.includes(review!.album_discogs_id) ? '⭐' : '☆')}
                </FavoriteButton>
              )}
              {user && review!.username === user.username && (
                <ActionButtons>
                  <ActionButton 
                    $variant="pin"
                    onClick={togglePin}
                    title={review!.is_pinned ? 'Unpin' : 'Pin'}
                  >
                    {review!.is_pinned ? '📌' : '📍'}
                  </ActionButton>
                  <ActionButton 
                    $variant="edit"
                    onClick={handleEdit}
                    title="Edit"
                  >
                    ✏️
                  </ActionButton>
                  <ActionButton 
                    $variant="delete"
                    onClick={handleDelete}
                    title="Delete"
                  >
                    🗑️
                  </ActionButton>
                </ActionButtons>
              )}
              <Rating>{review!.rating}/10</Rating>
            </RatingContainer>
          </TitleRatingRow>
          
          <ArtistSection>
            <ArtistPhoto 
              src={review!.album_artist_photo}
              alt={`${review!.album_artist} photo`}
              size="medium"
            />
            <ArtistName>
              {review!.album_artist}
              {review!.album_year && ` • ${review!.album_year}`}
            </ArtistName>
          </ArtistSection>
          
          {review!.user_genres && review!.user_genres.length > 0 && (
            <Genres>
              {review!.user_genres.map(genre => (
                <GenreTag key={genre.id}>{genre.name}</GenreTag>
              ))}
            </Genres>
          )}

          <AlbumMeta>
            <UserLikeLine>
              <ReviewerInfo onClick={() => navigate(`/users/${review!.username}`)}>
                <ReviewerAvatar 
                  src={review!.user_avatar || '/static/accounts/default-avatar.svg'} 
                  alt={review!.username}
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/static/accounts/default-avatar.svg';
                  }}
                />
                <span>
                  {review!.username}
                                     {review!.user_is_staff && (
                     <span 
                       style={{ 
                         marginLeft: '4px', 
                         fontSize: '18px',
                         color: '#3b82f6',
                         fontWeight: 'bold'
                       }}
                       title="Verified Staff"
                     >
                       ✓
                     </span>
                   )}
                </span>
              </ReviewerInfo>
              {review!.likes_count > 0 && (
                <>
                  <PipeSeparator>|</PipeSeparator>
                  <LikeCount onClick={() => navigate(`/review/${review!.id}/likes`)}>
                    ❤️ {review!.likes_count} {review!.likes_count === 1 ? 'like' : 'likes'}
                  </LikeCount>
                </>
              )}
            </UserLikeLine>
            <div>Reviewed on {new Date(review!.created_at).toLocaleDateString('en-US', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}</div>
          </AlbumMeta>
        </ReviewInfo>
      </ReviewHeader>

      <ReviewContent>
        {renderFormattedText(review!.content)}
      </ReviewContent>

      <CommentsSection>
        <CommentsHeader>Comments</CommentsHeader>
        
        {user && (
          <CommentForm>
            <FormattedTextEditor
              value={newComment}
              onChange={setNewComment}
              placeholder="Write a comment..."
              minHeight="120px"
              disabled={submittingComment}
            />
            <CommentSubmit 
              onClick={submitComment}
              disabled={!newComment.trim() || submittingComment}
            >
              {submittingComment ? 'Posting...' : 'Post Comment'}
            </CommentSubmit>
          </CommentForm>
        )}

        <CommentsList>
          {comments.length === 0 ? (
            <EmptyComments>
              No comments yet. Be the first to comment!
            </EmptyComments>
          ) : (
            comments.map(comment => (
              <CommentItem key={comment.id}>
                <CommentHeader>
                  <CommentUsername onClick={() => navigate(`/users/${comment.username}`)}>
                    {comment.username}
                    {comment.user_is_staff && (
                      <span 
                        style={{ 
                          marginLeft: '4px', 
                          fontSize: '14px',
                          color: '#3b82f6',
                          fontWeight: 'bold'
                        }}
                        title="Verified Staff"
                      >
                        ✓
                      </span>
                    )}
                  </CommentUsername>
                  <CommentTime>{getTimeAgo(comment.created_at)}</CommentTime>
                </CommentHeader>
                
                {editingCommentId === comment.id ? (
                  <CommentEditForm>
                    <CommentEditInput
                      value={editingCommentContent}
                      onChange={(e) => setEditingCommentContent(e.target.value)}
                      placeholder="Edit your comment..."
                    />
                    <CommentEditActions>
                      <CommentEditButton 
                        $variant="save"
                        onClick={() => saveEditComment(comment.id)}
                        disabled={!editingCommentContent.trim()}
                      >
                        Save
                      </CommentEditButton>
                      <CommentEditButton 
                        $variant="cancel"
                        onClick={cancelEditComment}
                      >
                        Cancel
                      </CommentEditButton>
                    </CommentEditActions>
                  </CommentEditForm>
                ) : (
                  <>
                    <CommentContent>{renderFormattedText(comment.content)}</CommentContent>
                    {user && comment.username === user.username && (
                      <CommentActions>
                        <CommentActionButton onClick={() => startEditComment(comment)}>
                          Edit
                        </CommentActionButton>
                        <CommentActionButton onClick={() => deleteComment(comment.id)}>
                          Delete
                        </CommentActionButton>
                      </CommentActions>
                    )}
                  </>
                )}
              </CommentItem>
            ))
          )}
        </CommentsList>
      </CommentsSection>

      {/* Edit Review Modal */}
      <EditReviewModal
        isVisible={showEditReviewModal}
        reviewId={review?.id || null}
        onClose={handleCloseEditReviewModal}
        onSave={handleSaveEditReview}
      />
    </Container>
  );
};

export default ReviewDetailPage; 
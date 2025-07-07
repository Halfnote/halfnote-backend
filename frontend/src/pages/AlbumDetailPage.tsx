import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';
import { musicAPI } from '../services/api';
import { formatDistanceToNow } from 'date-fns';
import EditReviewModal from '../components/EditReviewModal';
import { renderFormattedText } from '../utils/textFormatting';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
`;

const BackLink = styled.button`
  background: none;
  border: none;
  color: #667eea;
  font-size: 16px;
  cursor: pointer;
  margin-bottom: 20px;
  padding: 0;
  display: flex;
  align-items: center;
  gap: 5px;
  
  &:hover {
    text-decoration: underline;
  }
`;

const AlbumHeader = styled.div`
  display: flex;
  gap: 30px;
  margin-bottom: 40px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 20px;
  }
`;

const AlbumCover = styled.img`
  width: 300px;
  height: 300px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
  
  @media (max-width: 768px) {
    width: 250px;
    height: 250px;
    margin: 0 auto;
  }
`;

const AlbumInfo = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const AlbumTitle = styled.h1`
  font-size: 2.5em;
  font-weight: bold;
  color: #1f2937;
  margin: 0;
  
  @media (max-width: 768px) {
    font-size: 2em;
  }
`;

const AlbumArtist = styled.h2`
  font-size: 1.5em;
  color: #6b7280;
  margin: 0;
  font-weight: 500;
`;

const AlbumMeta = styled.div`
  display: flex;
  gap: 15px;
  align-items: center;
  color: #6b7280;
  font-size: 16px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
`;

const GenresList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
`;

const GenreTag = styled.span`
  background: #e5e7eb;
  color: #374151;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
`;

const Stats = styled.div`
  display: flex;
  gap: 20px;
  margin-top: 20px;
  color: #6b7280;
  
  @media (max-width: 768px) {
    gap: 15px;
  }
`;

const Stat = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const StatNumber = styled.div`
  font-size: 1.5em;
  font-weight: bold;
  color: #1f2937;
`;

const StatLabel = styled.div`
  font-size: 14px;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 15px;
  margin-top: 20px;
`;

const PrimaryButton = styled.button`
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover {
    background: #5a67d8;
  }
  
  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const SecondaryButton = styled.button`
  background: #e5e7eb;
  color: #374151;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover {
    background: #d1d5db;
  }
  
  &:disabled {
    background: #f3f4f6;
    cursor: not-allowed;
  }
`;

const ContentTabs = styled.div`
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 20px;
`;

const Tab = styled.button<{ $active: boolean }>`
  background: none;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  color: ${props => props.$active ? '#667eea' : '#6b7280'};
  border-bottom: ${props => props.$active ? '2px solid #667eea' : '2px solid transparent'};
  transition: color 0.2s, border-color 0.2s;
  
  &:hover {
    color: #667eea;
  }
`;

const TabContent = styled.div`
  min-height: 300px;
`;

const TrackList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const Track = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
`;

const TrackPosition = styled.div`
  font-weight: 500;
  color: #6b7280;
  min-width: 40px;
`;

const TrackInfo = styled.div`
  flex: 1;
`;

const TrackTitle = styled.div`
  font-weight: 500;
  color: #1f2937;
`;

const TrackArtist = styled.div`
  font-size: 14px;
  color: #6b7280;
`;

const TrackDuration = styled.div`
  color: #6b7280;
  font-size: 14px;
`;

const CreditsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const CreditGroup = styled.div`
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 15px;
  
  &:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }
`;

const Credit = styled.div`
  padding: 4px 0;
  padding-left: 20px;
`;

const CreditRole = styled.div`
  font-weight: 600;
  color: #374151;
  font-size: 16px;
  margin-bottom: 8px;
  border-bottom: 2px solid #f3f4f6;
  padding-bottom: 4px;
`;

const CreditName = styled.div`
  color: #6b7280;
  font-size: 15px;
`;

const ReviewsSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const ReviewItem = styled.div`
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  background: white;
`;

const ReviewHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
`;

const ReviewUser = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
`;

const ReviewAvatar = styled.img`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
`;

const ReviewUserInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const ReviewUsername = styled.div`
  font-weight: 500;
  color: #1f2937;
`;

const ReviewDate = styled.div`
  font-size: 14px;
  color: #6b7280;
`;

const ReviewRating = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #667eea;
`;

const ReviewContent = styled.div`
  color: #374151;
  line-height: 1.6;
  margin-bottom: 15px;
`;

const ReviewGenres = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
`;

const ReviewActions = styled.div`
  display: flex;
  gap: 15px;
  align-items: center;
`;

const ReviewAction = styled.button`
  background: none;
  border: none;
  color: #6b7280;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  
  &:hover {
    color: #667eea;
  }
`;

const LoadingDiv = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #6b7280;
`;

const ErrorMessage = styled.div`
  color: #dc2626;
  text-align: center;
  padding: 20px;
  background: #fef2f2;
  border-radius: 8px;
  margin: 20px 0;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px;
  color: #6b7280;
  
  h3 {
    margin-bottom: 10px;
    color: #374151;
  }
`;

const ReviewsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const ReviewSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const ReviewSectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
`;

const ReviewSectionTitle = styled.div`
  font-size: 18px;
  font-weight: bold;
  color: #1f2937;
`;

const ReviewSectionSubtitle = styled.div`
  font-size: 14px;
  color: #6b7280;
`;

const ShowMoreReviews = styled.button`
  background: none;
  border: none;
  color: #667eea;
  font-size: 14px;
  cursor: pointer;
  margin-top: 10px;
  align-self: center;
  
  &:hover {
    text-decoration: underline;
  }
`;

interface AlbumData {
  id?: string;
  title: string;
  artist: string;
  year?: number;
  cover_url?: string;
  cover_image?: string;
  discogs_id: string;
  genres?: string[];
  discogs_genres?: string[];
  discogs_styles?: string[];
  tracklist?: Array<{
    position: string;
    title: string;
    duration?: string;
    artists?: Array<{ name: string }>;
  }>;
  credits?: Array<{
    name: string;
    role: string;
  }>;
}

interface Review {
  id: number;
  username: string;
  user_avatar?: string;
  user_is_staff?: boolean;
  rating: number;
  content: string;
  created_at: string;
  is_pinned: boolean;
  likes_count: number;
  is_liked_by_user: boolean;
  comments_count: number;
  user_genres: Array<{ id: number; name: string }>;
}

interface AlbumDetailData {
  album: AlbumData;
  reviews: Review[];
  review_count: number;
  average_rating: number | null;
  exists_in_db: boolean;
  cached: boolean;
}

const AlbumDetailPage: React.FC = () => {
  const { discogsId } = useParams<{ discogsId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [albumData, setAlbumData] = useState<AlbumDetailData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'reviews' | 'tracklist' | 'credits'>('reviews');
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [userReview, setUserReview] = useState<Review | null>(null);
  const [likingReviews, setLikingReviews] = useState<Set<number>>(new Set());

  const loadAlbumData = useCallback(async () => {
    if (!discogsId) return;
    
    try {
      setLoading(true);
      setError('');
      const data = await musicAPI.getAlbumDetails(discogsId);
      setAlbumData(data);
      
      // Find current user's review if they have one
      if (user && data.reviews) {
        const myReview = data.reviews.find((review: Review) => review.username === user.username);
        setUserReview(myReview || null);
      }
    } catch (err: any) {
      console.error('Failed to load album data:', err);
      setError(err.message || 'Failed to load album details');
    } finally {
      setLoading(false);
    }
  }, [discogsId, user]);

  const handleWriteReview = () => {
    if (!user) {
      navigate('/login');
      return;
    }
    setShowReviewModal(true);
  };

  const handleLikeReview = async (reviewId: number) => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    if (likingReviews.has(reviewId)) return;
    
    setLikingReviews(prev => new Set(prev).add(reviewId));
    
    try {
      await musicAPI.likeReview(reviewId);
      
      // Update local state
      if (albumData) {
        setAlbumData({
          ...albumData,
          reviews: albumData.reviews.map(review => 
            review.id === reviewId 
              ? {
                  ...review,
                  is_liked_by_user: !review.is_liked_by_user,
                  likes_count: review.is_liked_by_user ? review.likes_count - 1 : review.likes_count + 1
                }
              : review
          )
        });
      }
    } catch (error) {
      console.error('Failed to like review:', error);
    } finally {
      setLikingReviews(prev => {
        const newSet = new Set(prev);
        newSet.delete(reviewId);
        return newSet;
      });
    }
  };

  const handleDeleteReview = async (reviewId: number) => {
    if (!window.confirm('Are you sure you want to delete this review?')) return;
    
    try {
      await musicAPI.deleteReview(reviewId);
      setUserReview(null);
      await loadAlbumData();
    } catch (error) {
      console.error('Failed to delete review:', error);
    }
  };

  const renderReviews = () => {
    if (!albumData?.reviews || albumData.reviews.length === 0) {
      return (
        <EmptyState>
          <h3>No reviews yet</h3>
          <p>Be the first to review this album!</p>
        </EmptyState>
      );
    }

    const reviews = albumData.reviews;
    
    // Get top reviews (reviews with most likes, minimum 1 like)
    const topReviews = reviews
      .filter(review => review.likes_count > 0)
      .sort((a, b) => b.likes_count - a.likes_count)
      .slice(0, 3); // Show top 3
    
    // Get recent reviews (sorted by creation date)
    const recentReviews = [...reviews]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5); // Show latest 5

    const renderReviewCard = (review: Review) => (
      <ReviewItem key={review.id}>
        <ReviewHeader>
          <ReviewUser>
            <ReviewAvatar 
              src={review.user_avatar || '/static/accounts/default-avatar.svg'} 
              alt={review.username || 'Unknown user'}
              onError={(e) => {
                (e.target as HTMLImageElement).src = '/static/accounts/default-avatar.svg';
              }}
            />
            <ReviewUserInfo>
              <ReviewUsername>
                {review.username || 'Unknown user'}
                {review.user_is_staff && (
                  <span 
                    style={{ 
                      marginLeft: '6px', 
                      fontSize: '14px',
                      color: '#3b82f6',
                      fontWeight: 'bold'
                    }}
                    title="Verified Staff"
                  >
                    ✓
                  </span>
                )}
              </ReviewUsername>
              <ReviewDate>
                {formatDistanceToNow(new Date(review.created_at), { addSuffix: true })}
              </ReviewDate>
            </ReviewUserInfo>
          </ReviewUser>
          <ReviewRating>
            {review.rating}/10
            {review.is_pinned && ' 📌'}
          </ReviewRating>
        </ReviewHeader>
        
        <ReviewContent>
          {renderFormattedText(review.content)}
        </ReviewContent>
        
        {review.user_genres && review.user_genres.length > 0 && (
          <ReviewGenres>
            {review.user_genres.map(genre => (
              <GenreTag key={genre.id || `genre-${genre.name}`}>
                {typeof genre === 'string' ? genre : (genre?.name || 'Unknown Genre')}
              </GenreTag>
            ))}
          </ReviewGenres>
        )}
        
        <ReviewActions>
          <ReviewAction
            onClick={() => handleLikeReview(review.id)}
            disabled={likingReviews.has(review.id)}
          >
            {review.is_liked_by_user ? '❤️' : '🤍'} {review.likes_count}
          </ReviewAction>
          <ReviewAction onClick={() => navigate(`/review/${review.id}`)}>
            💬 {review.comments_count}
          </ReviewAction>
          {user && user.username === review.username && (
            <>
              <ReviewAction onClick={() => setShowReviewModal(true)}>
                ✏️ Edit
              </ReviewAction>
              <ReviewAction onClick={() => handleDeleteReview(review.id)}>
                🗑️ Delete
              </ReviewAction>
            </>
          )}
        </ReviewActions>
      </ReviewItem>
    );

    return (
      <ReviewsContainer>
        {topReviews.length > 0 && (
          <ReviewSection>
            <ReviewSectionHeader>
              <ReviewSectionTitle>⭐ Top Reviews</ReviewSectionTitle>
              <ReviewSectionSubtitle>Most liked reviews</ReviewSectionSubtitle>
            </ReviewSectionHeader>
            <ReviewsSection>
              {topReviews.map(renderReviewCard)}
            </ReviewsSection>
          </ReviewSection>
        )}
        
        <ReviewSection>
          <ReviewSectionHeader>
            <ReviewSectionTitle>🕒 Recent Reviews</ReviewSectionTitle>
            <ReviewSectionSubtitle>Latest reviews</ReviewSectionSubtitle>
          </ReviewSectionHeader>
          <ReviewsSection>
            {recentReviews.map(renderReviewCard)}
          </ReviewsSection>
        </ReviewSection>
        
        {reviews.length > 5 && (
          <ShowMoreReviews onClick={() => navigate(`/albums/${albumData.album.discogs_id}/reviews`)}>
            View all {reviews.length} reviews →
          </ShowMoreReviews>
        )}
      </ReviewsContainer>
    );
  };

  const renderTracklist = () => {
    if (!albumData?.album.tracklist || albumData.album.tracklist.length === 0) {
      return (
        <EmptyState>
          <h3>No tracklist available</h3>
          <p>Tracklist information is not available for this album.</p>
        </EmptyState>
      );
    }

    return (
      <TrackList>
        {albumData.album.tracklist.map((track, index) => (
          <Track key={index}>
            <TrackPosition>{track.position || index + 1}</TrackPosition>
            <TrackInfo>
              <TrackTitle>{track.title}</TrackTitle>
              {track.artists && track.artists.length > 0 && (
                <TrackArtist>
                  {track.artists.map(artist => 
                    typeof artist === 'string' ? artist : (artist?.name || 'Unknown Artist')
                  ).join(', ')}
                </TrackArtist>
              )}
            </TrackInfo>
            {track.duration && <TrackDuration>{track.duration}</TrackDuration>}
          </Track>
        ))}
      </TrackList>
    );
  };

  const renderCredits = () => {
    if (!albumData?.album.credits || albumData.album.credits.length === 0) {
      return (
        <EmptyState>
          <h3>No credits available</h3>
          <p>Credit information is not available for this album.</p>
        </EmptyState>
      );
    }

    // Group credits by role
    const groupedCredits = albumData.album.credits.reduce((acc, credit) => {
      const role = typeof credit.role === 'string' ? credit.role : (credit?.role || 'Unknown Role');
      const name = typeof credit.name === 'string' ? credit.name : (credit?.name || 'Unknown Name');
      
      if (!acc[role]) {
        acc[role] = [];
      }
      acc[role].push(name);
      return acc;
    }, {} as Record<string, string[]>);

    return (
      <CreditsList>
        {Object.entries(groupedCredits).map(([role, names]) => (
          <CreditGroup key={role}>
            <CreditRole>{role}</CreditRole>
            {names.map((name, index) => (
              <Credit key={`${role}-${index}`}>
                <CreditName>{name}</CreditName>
              </Credit>
            ))}
          </CreditGroup>
        ))}
      </CreditsList>
    );
  };

  useEffect(() => {
    loadAlbumData();
  }, [loadAlbumData]);

  if (loading) {
    return (
      <Container>
        <LoadingDiv>Loading album details...</LoadingDiv>
      </Container>
    );
  }

  if (error || !albumData) {
    return (
      <Container>
        <BackLink onClick={() => navigate(-1)}>
          ← Back
        </BackLink>
        <ErrorMessage>
          {error || 'Album not found'}
        </ErrorMessage>
      </Container>
    );
  }

  const album = albumData.album;
  const genres = album.genres || album.discogs_genres || [];
  const styles = album.discogs_styles || [];

  // Prepare genres and styles as arrays of string or { name: string }
  const genresList: (string | { name: string })[] = Array.isArray(genres) ? genres : [];
  const stylesList: (string | { name: string })[] = Array.isArray(styles) ? styles : [];

  return (
    <Container>
      <BackLink onClick={() => navigate(-1)}>
        ← Back
      </BackLink>
      
      <AlbumHeader>
        <AlbumCover 
          src={album.cover_url || album.cover_image || '/static/music/default-album.svg'} 
          alt={album.title}
          onError={(e) => {
            (e.target as HTMLImageElement).src = '/static/music/default-album.svg';
          }}
        />
        
        <AlbumInfo>
          <AlbumTitle>{album.title}</AlbumTitle>
          <AlbumArtist>{album.artist}</AlbumArtist>
          
          <AlbumMeta>
            {album.year && <span>{album.year}</span>}
          </AlbumMeta>
          
          {(genresList.length > 0 || stylesList.length > 0) && (
            <GenresList>
              {genresList.map((genre, index) => (
                <GenreTag key={`genre-${index}`}>{typeof genre === 'string' ? genre : genre.name}</GenreTag>
              ))}
              {stylesList.map((style, index) => (
                <GenreTag key={`style-${index}`}>{typeof style === 'string' ? style : style.name}</GenreTag>
              ))}
            </GenresList>
          )}
          
          <Stats>
            <Stat>
              <StatNumber>{albumData.review_count}</StatNumber>
              <StatLabel>Reviews</StatLabel>
            </Stat>
            <Stat>
              <StatNumber>{albumData.average_rating ? albumData.average_rating.toFixed(1) : 'N/A'}</StatNumber>
              <StatLabel>Avg Rating</StatLabel>
            </Stat>
          </Stats>
          
          <ActionButtons>
            <PrimaryButton onClick={handleWriteReview}>
              {userReview ? 'Edit Review' : 'Write Review'}
            </PrimaryButton>
            <SecondaryButton onClick={() => navigate(`/search?q=${encodeURIComponent(album.artist)}`)}>
              More by {album.artist}
            </SecondaryButton>
          </ActionButtons>
        </AlbumInfo>
      </AlbumHeader>
      
      <ContentTabs>
        <Tab 
          $active={activeTab === 'reviews'} 
          onClick={() => setActiveTab('reviews')}
        >
          Reviews ({albumData.review_count})
        </Tab>
        <Tab 
          $active={activeTab === 'tracklist'} 
          onClick={() => setActiveTab('tracklist')}
        >
          Tracklist
        </Tab>
        <Tab 
          $active={activeTab === 'credits'} 
          onClick={() => setActiveTab('credits')}
        >
          Credits
        </Tab>
      </ContentTabs>
      
      <TabContent>
        {activeTab === 'reviews' && renderReviews()}
        {activeTab === 'tracklist' && renderTracklist()}
        {activeTab === 'credits' && renderCredits()}
      </TabContent>
      
      {showReviewModal && (
        <EditReviewModal
          isVisible={showReviewModal}
          reviewId={userReview?.id || null}
          onClose={() => setShowReviewModal(false)}
          onSave={async () => {
            await loadAlbumData();
            setShowReviewModal(false);
          }}
        />
      )}
    </Container>
  );
};

export default AlbumDetailPage; 
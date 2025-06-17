import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { musicAPI } from '../services/api';

interface User {
  id: number;
  username: string;
  name?: string;
  bio?: string;
  avatar?: string;
  follower_count?: number;
  following_count?: number;
  review_count?: number;
}

interface Review {
  id: number;
  username: string;
  album_title: string;
  album_artist: string;
  album_cover?: string;
  rating: number;
  content: string;
  created_at: string;
}

interface ReviewLikesData {
  review: Review;
  users: User[];
  total_count: number;
  has_more: boolean;
  next_offset?: number;
}

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
`;

const Header = styled.div`
  margin-bottom: 30px;
`;

const BackButton = styled.button`
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  margin-bottom: 20px;
  
  &:hover {
    color: #374151;
  }
`;

const ReviewInfo = styled.div`
  display: flex;
  gap: 20px;
  align-items: flex-start;
`;

const AlbumCover = styled.img`
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
`;

const ReviewDetails = styled.div`
  flex: 1;
`;

const AlbumTitle = styled.h2`
  margin: 0 0 5px 0;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
`;

const ArtistName = styled.div`
  color: #6b7280;
  margin-bottom: 10px;
`;

const ReviewMeta = styled.div`
  color: #6b7280;
  font-size: 14px;
`;

const Title = styled.h1`
  margin: 20px 0;
  font-size: 24px;
  font-weight: 600;
  color: #111827;
`;

const UsersGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const UserCard = styled.div`
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  }
`;

const UserAvatar = styled.img`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  margin: 0 auto 12px;
  display: block;
`;

const UserName = styled.h3`
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
`;

const Username = styled.div`
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #6b7280;
`;

const UserStats = styled.div`
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
`;

const LoadingDiv = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  flex-direction: column;
  gap: 16px;
`;

const ErrorDiv = styled.div`
  text-align: center;
  color: #ef4444;
  padding: 20px;
`;

const LoadMoreButton = styled.button`
  display: block;
  margin: 0 auto;
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  
  &:hover {
    background: #5a67d8;
  }
  
  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const Spinner = styled.div`
  border: 3px solid #f3f4f6;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ReviewLikesPage: React.FC = () => {
  const { reviewId } = useParams<{ reviewId: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<ReviewLikesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');
  const [allUsers, setAllUsers] = useState<User[]>([]);

  useEffect(() => {
    if (reviewId) {
      loadLikes();
    }
  }, [reviewId]);

  const loadLikes = async (offset = 0) => {
    if (!reviewId) return;
    
    const isLoadingMore = offset > 0;
    isLoadingMore ? setLoadingMore(true) : setLoading(true);
    setError('');
    
    try {
      const response = await musicAPI.getReviewLikesPage(parseInt(reviewId), offset);
      
      if (offset === 0) {
        setData(response);
        setAllUsers(response.users);
      } else {
        setData(prev => prev ? {
          ...prev,
          users: response.users,
          has_more: response.has_more,
          next_offset: response.next_offset
        } : response);
        setAllUsers(prev => [...prev, ...response.users]);
      }
    } catch (error: any) {
      console.error('Error loading likes:', error);
      setError(error.message || 'Failed to load likes');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleUserClick = (username: string) => {
    navigate(`/users/${username}`);
  };

  const handleLoadMore = () => {
    if (data?.next_offset) {
      loadLikes(data.next_offset);
    }
  };

  if (loading) {
    return (
      <Container>
        <LoadingDiv>
          <Spinner />
          <p>Loading likes...</p>
        </LoadingDiv>
      </Container>
    );
  }

  if (error || !data) {
    return (
      <Container>
        <ErrorDiv>
          {error || 'Failed to load likes'}
        </ErrorDiv>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <BackButton onClick={() => navigate(`/review/${reviewId}`)}>
          ← Back to Review
        </BackButton>
        
        <ReviewInfo>
          <AlbumCover 
            src={data.review.album_cover || '/static/accounts/default-avatar.svg'}
            alt={data.review.album_title}
            onError={(e) => {
              (e.target as HTMLImageElement).src = '/static/accounts/default-avatar.svg';
            }}
          />
          <ReviewDetails>
            <AlbumTitle>{data.review.album_title}</AlbumTitle>
            <ArtistName>{data.review.album_artist}</ArtistName>
            <ReviewMeta>
              Reviewed by {data.review.username}
            </ReviewMeta>
          </ReviewDetails>
        </ReviewInfo>
        
        <Title>
          {data.total_count} {data.total_count === 1 ? 'Like' : 'Likes'}
        </Title>
      </Header>
      
      <UsersGrid>
        {allUsers.map(user => (
          <UserCard key={user.id} onClick={() => handleUserClick(user.username)}>
            <UserAvatar 
              src={user.avatar || '/static/accounts/default-avatar.svg'}
              alt={user.username}
              onError={(e) => {
                (e.target as HTMLImageElement).src = '/static/accounts/default-avatar.svg';
              }}
            />
            <UserName>{user.name || user.username}</UserName>
            <Username>@{user.username}</Username>
            <UserStats>
              {user.review_count || 0} reviews • {user.follower_count || 0} followers • {user.following_count || 0} following
            </UserStats>
          </UserCard>
        ))}
      </UsersGrid>
      
      {data.has_more && (
        <LoadMoreButton 
          onClick={handleLoadMore}
          disabled={loadingMore}
        >
          {loadingMore ? 'Loading...' : 'Load More'}
        </LoadMoreButton>
      )}
    </Container>
  );
};

export default ReviewLikesPage; 
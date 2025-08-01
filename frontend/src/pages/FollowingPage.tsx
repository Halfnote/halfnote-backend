import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { userAPI, User } from '../services/api';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
`;

const BackLink = styled.button`
  background: none;
  border: none;
  color: #6b7280;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    color: #374151;
  }
`;

const PageHeader = styled.div`
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const PageTitle = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
`;

const PageSubtitle = styled.p`
  color: #6b7280;
  font-size: 16px;
`;

const UsersList = styled.div`
  display: grid;
  gap: 16px;
`;

const UserCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    border-color: #d1d5db;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
`;

const UserAvatar = styled.img`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
`;

const UserInfo = styled.div`
  flex: 1;
`;

const Username = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const VerifiedBadge = styled.span`
  color: #1d4ed8;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
`;

const UserStats = styled.div`
  color: #6b7280;
  font-size: 14px;
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

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;

  h3 {
    font-size: 18px;
    margin-bottom: 8px;
    color: #374151;
  }

  p {
    font-size: 14px;
  }
`;

const FollowingPage: React.FC = () => {
  const { username } = useParams<{ username: string }>();
  const navigate = useNavigate();
  const [following, setFollowing] = useState<User[]>([]);
  const [profileUser, setProfileUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadFollowing = async () => {
      if (!username) return;
      
      setLoading(true);
      setError('');
      
      try {
        const [followingData, profileData] = await Promise.all([
          userAPI.getFollowing(username),
          userAPI.getProfile(username)
        ]);
        setFollowing(Array.isArray(followingData) ? followingData : []);
        setProfileUser(profileData);
      } catch (error: any) {
        console.error('Error loading following:', error);
        setError(error.message || 'Failed to load following');
      } finally {
        setLoading(false);
      }
    };

    loadFollowing();
  }, [username]);

  if (loading) {
    return (
      <Container>
        <LoadingDiv>
          <Spinner />
          <p>Loading following...</p>
        </LoadingDiv>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <BackLink onClick={() => navigate(-1)}>
          ← Back
        </BackLink>
        <ErrorMessage>
          {error}
        </ErrorMessage>
      </Container>
    );
  }

  return (
    <Container>
      <BackLink onClick={() => navigate(`/users/${username}`)}>
        ← Back to {username}'s profile
      </BackLink>
      
      <PageHeader>
        <PageTitle>People {profileUser?.name || username} follows</PageTitle>
        <PageSubtitle>Users that {profileUser?.name || username} is following</PageSubtitle>
      </PageHeader>

      {following.length === 0 ? (
        <EmptyState>
          <h3>Not following anyone yet</h3>
          <p>{profileUser?.name || username} isn't following anyone yet.</p>
        </EmptyState>
      ) : (
        <UsersList>
          {following.map(user => (
            <UserCard key={user.id} onClick={() => navigate(`/users/${user.username}`)}>
              <UserAvatar 
                src={user.avatar || '/static/accounts/default-avatar.svg'} 
                alt={user.username}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/static/accounts/default-avatar.svg';
                }}
              />
              <UserInfo>
                <Username>
                  {user.username}
                  {user.is_staff && <VerifiedBadge>✓</VerifiedBadge>}
                </Username>
                <UserStats>
                  {user.review_count || 0} reviews • {user.follower_count || 0} followers • {user.following_count || 0} following
                </UserStats>
              </UserInfo>
            </UserCard>
          ))}
        </UsersList>
      )}
    </Container>
  );
};

export default FollowingPage; 
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { musicAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
`;

const BackLink = styled.a`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  text-decoration: none;
  margin-bottom: 24px;
  font-weight: 500;
  transition: color 0.2s ease;
  cursor: pointer;

  &:hover {
    color: #111827;
  }
`;

const ActivityHeader = styled.div`
  margin-bottom: 30px;
  text-align: center;
`;

const ActivityTitle = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
`;

const ActivitySubtitle = styled.p`
  color: #6b7280;
  font-size: 16px;
`;

const ActivityTabs = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  justify-content: center;
`;

const ActivityTabBtn = styled.button<{ $active: boolean }>`
  padding: 8px 20px;
  border: 1px solid #e5e7eb;
  background: ${props => props.$active ? '#111827' : 'white'};
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  color: ${props => props.$active ? 'white' : '#374151'};
  border-color: ${props => props.$active ? '#111827' : '#e5e7eb'};

  &:hover {
    background: ${props => props.$active ? '#374151' : '#f9fafb'};
  }
`;

const ActivityFeed = styled.div`
  background: white;
  border-radius: 16px;
  padding: 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #e5e7eb;
  overflow: hidden;
`;

const ActivityItem = styled.div`
  display: flex;
  align-items: flex-start;
  padding: 20px 24px;
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 0.2s ease;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background-color: #f9fafb;
  }
`;

const ActivityAvatar = styled.img`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin-right: 16px;
  object-fit: cover;
  flex-shrink: 0;
`;

const ActivityContent = styled.div`
  flex: 1;
  min-width: 0;
`;

const ActivityText = styled.div`
  margin-bottom: 8px;
  line-height: 1.5;
  font-size: 15px;
`;

const ActivityUser = styled.span`
  font-weight: 600;
  color: #111827;
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
`;

const ActivityAlbum = styled.span`
  font-weight: 600;
  color: #667eea;
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
`;

const ActivityTime = styled.div`
  color: #9ca3af;
  font-size: 14px;
  margin-bottom: 8px;
`;

const ReviewContent = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 8px;
  font-style: italic;
  color: #4b5563;
  font-size: 14px;
  line-height: 1.4;
  border-left: 3px solid #e5e7eb;
`;

const CommentContent = styled.div`
  background: #f0f9ff;
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 8px;
  font-style: italic;
  color: #1e40af;
  font-size: 14px;
  line-height: 1.4;
  border-left: 3px solid #3b82f6;
`;

const ActivityMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
`;

const AlbumCover = styled.img`
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
  margin-left: 16px;
  cursor: pointer;
  transition: transform 0.2s ease;

  &:hover {
    transform: scale(1.05);
  }
`;

const LoadingDiv = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
`;

const Spinner = styled.div`
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-radius: 50%;
  border-top-color: #111827;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 16px;

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
`;

const NoActivity = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;

  h3 {
    font-size: 20px;
    margin-bottom: 8px;
  }
`;

interface Activity {
  id: number;
  user: {
    username: string;
    avatar?: string;
    is_staff?: boolean;
  };
  target_user?: {
    username: string;
    avatar?: string;
    is_staff?: boolean;
  };
  activity_type: string;
  created_at: string;
  review_details?: {
    id: number;
    album: {
      title: string;
      artist: string;
      year?: number;
      cover_url?: string;
    };
    rating: number;
    content: string;
    user: {
      username: string;
      avatar?: string;
      is_staff?: boolean;
    };
  };
  comment_details?: {
    id: number;
    content: string;
    created_at: string;
  };
}

const ActivityPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'friends' | 'you' | 'incoming'>('friends');

  const loadActivities = useCallback(async () => {
    if (!user) return;
    
    setLoading(true);
    setError('');
    
    try {
      const data = await musicAPI.getActivityFeed(activeTab);
      setActivities(data || []);
    } catch (error: any) {
      console.error('Error loading activities:', error);
      setActivities([]);
      setError('');
    } finally {
      setLoading(false);
    }
  }, [user, activeTab]);

  useEffect(() => {
    loadActivities();
  }, [loadActivities]);

  const formatTime = (dateString: string) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      const hours = Math.floor(diff / 3600000);
      const days = Math.floor(diff / 86400000);

      if (days > 0) return `${days}d ago`;
      if (hours > 0) return `${hours}h ago`;
      return 'Just now';
    } catch (error) {
      return 'Unknown time';
    }
  };

  const renderUsername = (username: string, isStaff?: boolean, navigateToUser?: boolean) => {
    return (
      <>
        {navigateToUser ? (
          <ActivityUser onClick={() => navigate(`/users/${username}`)}>
            {username}
          </ActivityUser>
        ) : (
          username
        )}
        {isStaff && (
          <span 
            style={{ 
              marginLeft: '4px', 
              fontSize: '12px',
              color: '#3b82f6'
            }}
            title="Verified Staff"
          >
            ✓
          </span>
        )}
      </>
    );
  };

  const renderActivityText = (activity: Activity) => {
    try {
      const isCurrentUser = activity.user.username === user?.username;
      const isTargetCurrentUser = activity.target_user?.username === user?.username;
      const isReviewOwnerCurrentUser = activity.review_details?.user?.username === user?.username;

      switch (activity.activity_type) {
        case 'review_created':
          return (
            <>
              {isCurrentUser ? (
                <span style={{ fontWeight: 600, color: '#111827' }}>You</span>
              ) : (
                renderUsername(activity.user.username, activity.user.is_staff, true)
              )}
              {' reviewed '}
              <ActivityAlbum onClick={() => navigate(`/review/${activity.review_details?.id}/`)}>
                {activity.review_details?.album.title || 'an album'}
              </ActivityAlbum>
              {activity.review_details?.album.artist && ` by ${activity.review_details.album.artist}`}
              {activity.review_details?.album.year && ` (${activity.review_details.album.year})`}
              {activity.review_details?.rating && ` and rated it ${activity.review_details.rating}/10`}
            </>
          );
        case 'user_followed':
          return (
            <>
              {isCurrentUser ? (
                <span style={{ fontWeight: 600, color: '#111827' }}>You</span>
              ) : (
                <ActivityUser onClick={() => navigate(`/users/${activity.user.username}`)}>
                  {activity.user.username}
                </ActivityUser>
              )}
              {' started following '}
              {activity.target_user ? (
                isTargetCurrentUser ? (
                  <span style={{ fontWeight: 600, color: '#111827' }}>you</span>
                ) : (
                  <ActivityUser onClick={() => navigate(`/users/${activity.target_user!.username}`)}>
                    {activity.target_user!.username}
                  </ActivityUser>
                )
              ) : 'someone'}
            </>
          );
        case 'review_liked':
          return (
            <>
              {isCurrentUser ? (
                <span style={{ fontWeight: 600, color: '#111827' }}>You</span>
              ) : (
                <ActivityUser onClick={() => navigate(`/users/${activity.user.username}`)}>
                  {activity.user.username}
                </ActivityUser>
              )}
              {' liked '}
              {activity.review_details?.user?.username && (
                isReviewOwnerCurrentUser ? (
                  <span style={{ fontWeight: 600, color: '#111827' }}>your</span>
                ) : isCurrentUser ? (
                  <>
                    <ActivityUser onClick={() => navigate(`/users/${activity.review_details!.user!.username}`)}>
                      {activity.review_details!.user!.username}
                    </ActivityUser>
                    <span>'s</span>
                  </>
                ) : (
                  <>
                    <ActivityUser onClick={() => navigate(`/users/${activity.review_details!.user!.username}`)}>
                      {activity.review_details!.user!.username}
                    </ActivityUser>
                    <span>'s</span>
                  </>
                )
              )}
              {' review of '}
              <ActivityAlbum onClick={() => navigate(`/review/${activity.review_details?.id}/`)}>
                {activity.review_details?.album?.title || 'an album'}
              </ActivityAlbum>
            </>
          );
        case 'comment_created':
          return (
            <>
              {isCurrentUser ? (
                <span style={{ fontWeight: 600, color: '#111827' }}>You</span>
              ) : (
                <ActivityUser onClick={() => navigate(`/users/${activity.user.username}`)}>
                  {activity.user.username}
                </ActivityUser>
              )}
              {' commented on '}
              {activity.review_details?.user?.username && (
                isReviewOwnerCurrentUser ? (
                  <span style={{ fontWeight: 600, color: '#111827' }}>your</span>
                ) : isCurrentUser ? (
                  <>
                    <ActivityUser onClick={() => navigate(`/users/${activity.review_details!.user!.username}`)}>
                      {activity.review_details!.user!.username}
                    </ActivityUser>
                    <span>'s</span>
                  </>
                ) : activity.user.username === activity.review_details!.user!.username ? (
                  <span style={{ fontWeight: 600, color: '#111827' }}>their</span>
                ) : (
                  <>
                    <ActivityUser onClick={() => navigate(`/users/${activity.review_details!.user!.username}`)}>
                      {activity.review_details!.user!.username}
                    </ActivityUser>
                    <span>'s</span>
                  </>
                )
              )}
              {' review of '}
              <ActivityAlbum onClick={() => navigate(`/review/${activity.review_details?.id}/`)}>
                {activity.review_details?.album?.title || 'a review'}
              </ActivityAlbum>
            </>
          );
        default:
          return (
            <>
              {isCurrentUser ? (
                <span style={{ fontWeight: 600, color: '#111827' }}>You</span>
              ) : (
                <ActivityUser onClick={() => navigate(`/users/${activity.user.username}`)}>
                  {activity.user.username}
                </ActivityUser>
              )}
              {' performed an action'}
            </>
          );
      }
    } catch (error) {
      return `${activity.user?.username || 'Someone'} performed an action`;
    }
  };

  if (!user) {
    return (
      <Container>
        <BackLink onClick={() => navigate('/')}>
          ← Back to Home
        </BackLink>
        <ActivityHeader>
          <ActivityTitle>Activity Feed</ActivityTitle>
          <ActivitySubtitle>Please log in to see your activity feed</ActivitySubtitle>
        </ActivityHeader>
      </Container>
    );
  }

  return (
    <Container>
      <BackLink onClick={() => navigate('/')}>
        ← Back to Home
      </BackLink>

      <ActivityHeader>
        <ActivityTitle>Activity Feed</ActivityTitle>
      </ActivityHeader>

      <ActivityTabs>
        <ActivityTabBtn 
          $active={activeTab === 'friends'}
          onClick={() => setActiveTab('friends')}
        >
          Friends
        </ActivityTabBtn>
        <ActivityTabBtn 
          $active={activeTab === 'you'}
          onClick={() => setActiveTab('you')}
        >
          You
        </ActivityTabBtn>
        <ActivityTabBtn 
          $active={activeTab === 'incoming'}
          onClick={() => setActiveTab('incoming')}
        >
          Incoming
        </ActivityTabBtn>
      </ActivityTabs>



      <ActivityFeed>
        {loading ? (
          <LoadingDiv>
            <Spinner />
            <p>Loading activities...</p>
          </LoadingDiv>
        ) : activities.length === 0 ? (
          <NoActivity>
            <h3>No activity yet</h3>
            <p>
              {activeTab === 'friends' 
                ? 'Start following people to see their activity!'
                : activeTab === 'you'
                ? 'Create some reviews to see your activity here!'
                : 'No incoming activity yet!'
              }
            </p>
          </NoActivity>
        ) : (
          activities.map((activity) => (
            <ActivityItem key={activity.id}>
              <ActivityAvatar 
                src={activity.user?.avatar || '/static/accounts/default-avatar.svg'} 
                alt={activity.user?.username || 'User'}
                                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/static/accounts/default-avatar.svg';
                  }}
              />
              <ActivityContent>
                <ActivityText>
                  {renderActivityText(activity)}
                </ActivityText>
                <ActivityTime>{formatTime(activity.created_at)}</ActivityTime>
                
                {/* Show review content for review activities */}
                {activity.activity_type === 'review_created' && activity.review_details?.content && (
                  <ReviewContent>
                    "{activity.review_details.content}"
                  </ReviewContent>
                )}
                
                {/* Show comment content for comment activities */}
                {activity.comment_details && (
                  <CommentContent>
                    "{activity.comment_details.content}"
                  </CommentContent>
                )}
              </ActivityContent>
              
              {/* Show album cover for review-related activities */}
              {activity.review_details?.album?.cover_url && (
                <AlbumCover 
                  src={activity.review_details.album.cover_url}
                  alt={activity.review_details.album.title}
                  onClick={() => navigate(`/review/${activity.review_details?.id}/`)}
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              )}
            </ActivityItem>
          ))
        )}
      </ActivityFeed>
    </Container>
  );
};

export default ActivityPage; 
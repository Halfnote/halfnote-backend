import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';

interface User {
  id: number;
  username: string;
  name?: string;
  bio?: string;
  avatar?: string;
  follower_count?: number;
  following_count?: number;
  review_count?: number;
  is_staff?: boolean;
}

interface List {
  id: number;
  name: string;
  description?: string;
  user: {
    username: string;
    avatar?: string;
  };
  album_count: number;
  likes_count: number;
}

interface ListLikesData {
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

const ListInfo = styled.div`
  display: flex;
  gap: 20px;
  align-items: flex-start;
`;

const ListIcon = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32px;
  font-weight: bold;
`;

const ListDetails = styled.div`
  flex: 1;
`;

const ListTitle = styled.h2`
  margin: 0 0 5px 0;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
`;

const ListCreator = styled.div`
  color: #6b7280;
  margin-bottom: 10px;
`;

const ListMeta = styled.div`
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

const ListLikesPage: React.FC = () => {
  const { listId } = useParams<{ listId: string }>();
  const navigate = useNavigate();
  
  const [list, setList] = useState<List | null>(null);
  const [likesData, setLikesData] = useState<ListLikesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState('');

  const loadList = async () => {
    if (!listId) return;
    
    try {
      const response = await fetch(`/api/music/lists/${listId}/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setList(data);
      } else {
        setError('List not found');
      }
    } catch (err) {
      setError('Failed to load list');
    }
  };

  const loadLikes = async (offset = 0) => {
    if (!listId) return;
    
    if (offset === 0) {
      setLoading(true);
    } else {
      setLoadingMore(true);
    }
    
    try {
      const response = await fetch(`/api/music/lists/${listId}/likes/?offset=${offset}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        
        if (offset === 0) {
          setLikesData(data);
        } else {
          setLikesData(prev => prev ? {
            ...data,
            users: [...prev.users, ...data.users]
          } : data);
        }
      } else {
        setError('Failed to load likes');
      }
    } catch (err) {
      setError('Failed to load likes');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleUserClick = (username: string) => {
    navigate(`/users/${username}`);
  };

  const handleLoadMore = () => {
    if (likesData?.next_offset) {
      loadLikes(likesData.next_offset);
    }
  };

  useEffect(() => {
    loadList();
    loadLikes();
  }, [listId]);

  if (loading) {
    return (
      <Container>
        <LoadingDiv>
          <Spinner />
          <div>Loading likes...</div>
        </LoadingDiv>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <ErrorDiv>{error}</ErrorDiv>
      </Container>
    );
  }

  if (!list || !likesData) {
    return (
      <Container>
        <ErrorDiv>List or likes data not found</ErrorDiv>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <BackButton onClick={() => navigate(`/lists/${listId}`)}>
          ← Back to List
        </BackButton>
        
        <ListInfo>
          <ListIcon>
            📝
          </ListIcon>
          <ListDetails>
            <ListTitle>{list.name}</ListTitle>
            <ListCreator>by {list.user.username}</ListCreator>
            <ListMeta>
              {list.album_count} {list.album_count === 1 ? 'album' : 'albums'} • {list.likes_count} {list.likes_count === 1 ? 'like' : 'likes'}
            </ListMeta>
          </ListDetails>
        </ListInfo>
        
        <Title>
          {likesData.total_count} {likesData.total_count === 1 ? 'Like' : 'Likes'}
        </Title>
      </Header>

      {likesData.users.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          No likes yet.
        </div>
      ) : (
        <>
          <UsersGrid>
            {likesData.users.map(user => (
              <UserCard key={user.id} onClick={() => handleUserClick(user.username)}>
                <UserAvatar 
                  src={user.avatar || '/static/accounts/default-avatar.svg'}
                  alt={user.username}
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/static/accounts/default-avatar.svg';
                  }}
                />
                <UserName>
                  {user.name || user.username}
                  {user.is_staff && (
                    <span 
                      style={{ 
                        marginLeft: '4px', 
                        fontSize: '12px',
                        color: '#3b82f6',
                        fontWeight: 'bold'
                      }}
                      title="Verified Staff"
                    >
                      ✓
                    </span>
                  )}
                </UserName>
                <Username>@{user.username}</Username>
                <UserStats>
                  {user.review_count || 0} reviews • {user.follower_count || 0} followers • {user.following_count || 0} following
                </UserStats>
              </UserCard>
            ))}
          </UsersGrid>

          {likesData.has_more && (
            <LoadMoreButton 
              onClick={handleLoadMore}
              disabled={loadingMore}
            >
              {loadingMore ? 'Loading...' : 'Load More'}
            </LoadMoreButton>
          )}
        </>
      )}
    </Container>
  );
};

export default ListLikesPage; 
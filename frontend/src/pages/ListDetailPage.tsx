import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
`;

const Header = styled.div`
  margin-bottom: 40px;
`;

const ListTitle = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 12px;
`;

const ListMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 16px;
  color: #6b7280;
  font-size: 14px;
`;

const ListDescription = styled.p`
  color: #4b5563;
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 24px;
`;

const ActionsBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
`;

const SearchSection = styled.div`
  display: flex;
  gap: 12px;
  flex: 1;
  max-width: 500px;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #ff6b35;
    box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
  }
`;

const SearchButton = styled.button`
  background: #ff6b35;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
  
  &:hover {
    background: #e55a31;
  }
  
  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const LikeButton = styled.button<{ $isLiked: boolean }>`
  background: ${props => props.$isLiked ? '#ef4444' : '#f3f4f6'};
  color: ${props => props.$isLiked ? 'white' : '#374151'};
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.$isLiked ? '#dc2626' : '#e5e7eb'};
  }
`;

const EditButton = styled.button`
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
  
  &:hover {
    background: #4b5563;
  }
`;

const DeleteButton = styled.button`
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
  
  &:hover {
    background: #dc2626;
  }
  
  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const SearchResults = styled.div`
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  margin-bottom: 32px;
  max-height: 400px;
  overflow-y: auto;
`;

const SearchResultItem = styled.div`
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background 0.2s ease;
  
  &:hover {
    background: #f9fafb;
  }
  
  &:last-child {
    border-bottom: none;
  }
`;

const AlbumCover = styled.img`
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  margin-right: 16px;
  border: 1px solid #e5e7eb;
`;

const AlbumInfo = styled.div`
  flex: 1;
`;

const AlbumTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
`;

const AlbumArtist = styled.p`
  color: #6b7280;
  font-size: 14px;
`;

const AddButton = styled.button`
  background: #10b981;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
  
  &:hover {
    background: #059669;
  }
  
  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const AlbumsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
`;

const AlbumCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
  cursor: pointer;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const CardAlbumCover = styled.img`
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  object-fit: cover;
  margin-bottom: 12px;
  border: 1px solid #e5e7eb;
`;

const CardAlbumTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
  line-height: 1.3;
`;

const CardAlbumArtist = styled.p`
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 8px;
`;

const ReviewInfo = styled.div`
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
  padding: 8px;
  font-size: 12px;
  color: #166534;
`;

const RemoveButton = styled.button`
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s ease;
  
  &:hover {
    background: rgba(220, 38, 38, 0.9);
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
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #ff6b35;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
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
`;

const ErrorMessage = styled.div`
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
`;



const ListDetailPage: React.FC = () => {
  const { listId } = useParams<{ listId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [list, setList] = useState<any>(null);
  const [albums, setAlbums] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [addingAlbum, setAddingAlbum] = useState<Set<number>>(new Set());
  
  const [removingAlbum, setRemovingAlbum] = useState<number | null>(null);
  const [liking, setLiking] = useState(false);

  const [newAlbumId, setNewAlbumId] = useState('');

  const loadList = useCallback(async () => {
    if (!listId) return;
    
    try {
      const response = await fetch(`/api/music/lists/${listId}/`, {
        headers: {
          'Authorization': user ? `Bearer ${localStorage.getItem('access_token')}` : '',
        },
      });
      
             if (response.ok) {
        const listData = await response.json();
        setList(listData);
        // Extract albums from items array
        const albumsFromItems = (listData.items || []).map((item: any) => ({
          ...item.album,
          user_review_id: item.album.user_review_id, // Include if backend provides this
        }));
        setAlbums(albumsFromItems);
       } else if (response.status === 404) {
        setError('List not found');
      } else {
        setError('Failed to load list');
      }
    } catch (err) {
      console.error('Failed to load list:', err);
      setError('Failed to load list');
    }
  }, [listId, user]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setSearching(true);
    try {
      const response = await fetch(`/api/music/search/?q=${encodeURIComponent(searchQuery)}`, {
        headers: {
          'Authorization': user ? `Bearer ${localStorage.getItem('access_token')}` : '',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results || []);
      }
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setSearching(false);
    }
  };

  const handleAddAlbum = async (album: any) => {
    if (!listId || addingAlbum.has(album.discogs_id)) return;
    
          setAddingAlbum(prev => new Set(prev).add(album.discogs_id));
    try {
      const response = await fetch(`/api/music/lists/${listId}/albums/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ discogs_id: album.discogs_id }),
      });

      if (response.ok) {
        await loadList(); // Reload to get updated list
        setSearchResults([]); // Clear search results
        setSearchQuery('');
      } else {
        const errorData = await response.json();
        alert(errorData.error || 'Failed to add album to list');
      }
    } catch (err) {
      console.error('Failed to add album:', err);
      alert('Failed to add album to list');
    } finally {
      setAddingAlbum(prev => {
        const newSet = new Set(prev);
        newSet.delete(album.discogs_id);
        return newSet;
      });
    }
  };

  const handleRemoveAlbum = async (album: any) => {
    if (!listId) return;
    
    try {
      const response = await fetch(`/api/music/lists/${listId}/albums/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ 
          album_id: album.id,  // Use the database UUID
          discogs_id: album.discogs_id  // Also send Discogs ID as fallback
        }),
      });

      if (response.ok) {
        setAlbums(prev => prev.filter(a => a.id !== album.id));
      } else {
        alert('Failed to remove album from list');
      }
    } catch (err) {
      console.error('Failed to remove album:', err);
      alert('Failed to remove album from list');
    }
  };

  const handleLikeList = async () => {
    if (!listId || liking) return;
    
    setLiking(true);
    try {
      const response = await fetch(`/api/music/lists/${listId}/like/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setList((prev: any) => ({
          ...prev,
          is_liked_by_user: data.status === 'liked',
          likes_count: data.likes_count,
        }));
      }
    } catch (err) {
      console.error('Failed to like list:', err);
    } finally {
      setLiking(false);
    }
  };

  const handleDeleteList = async () => {
    if (!listId || liking) return;
    
    if (!window.confirm('Are you sure you want to delete this list? This action cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(`/api/music/lists/${listId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        // Navigate back to profile
        navigate(`/users/${user?.username}`);
      } else {
        alert('Failed to delete list');
      }
    } catch (err) {
      console.error('Failed to delete list:', err);
      alert('Failed to delete list');
    }
  };

  const handleAlbumClick = (album: any) => {
    // If the user has a review for this album, navigate to the review
    if (album.user_review_id) {
      navigate(`/review/${album.user_review_id}`);
    }
    // If no review, could navigate to album detail page or show album info modal
    // For now, do nothing if no review exists
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await loadList();
      setLoading(false);
    };
    
    loadData();
  }, [loadList]);

  if (loading) {
    return (
      <Container>
        <LoadingDiv>
          <Spinner />
          <p>Loading list...</p>
        </LoadingDiv>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <ErrorMessage>{error}</ErrorMessage>
      </Container>
    );
  }

  if (!list) {
    return (
      <Container>
        <EmptyState>
          <h3>List not found</h3>
          <p>The list you're looking for doesn't exist or you don't have access to it.</p>
        </EmptyState>
      </Container>
    );
  }

  const isOwner = user?.username === list.user?.username;

  return (
    <Container>
      <Header>
        <ListTitle>{list.name}</ListTitle>
        <ListMeta>
          <span>By {list.user?.username}</span>
          <span>{albums.length} {albums.length === 1 ? 'album' : 'albums'}</span>
          <span 
            style={{ cursor: 'pointer', textDecoration: 'underline' }}
            onClick={() => navigate(`/lists/${listId}/likes`)}
          >
            {list.likes_count} {list.likes_count === 1 ? 'like' : 'likes'}
          </span>
        </ListMeta>
        {list.description && (
          <ListDescription>{list.description}</ListDescription>
        )}
      </Header>

      <ActionsBar>
        {isOwner ? (
          <SearchSection>
            <SearchInput
              type="text"
              placeholder="Search for albums to add..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <SearchButton 
              onClick={handleSearch}
              disabled={searching || !searchQuery.trim()}
            >
              {searching ? 'Searching...' : 'Search'}
            </SearchButton>
          </SearchSection>
        ) : (
          <div />
        )}
        
        <div style={{ display: 'flex', gap: '12px' }}>
          <LikeButton 
            $isLiked={list.is_liked_by_user}
            onClick={handleLikeList}
            disabled={liking}
          >
            {list.is_liked_by_user ? '❤️ Liked' : '🤍 Like'}
          </LikeButton>
          {isOwner && (
            <>
              <EditButton onClick={() => navigate(`/lists/${listId}/edit`)}>
                Edit List
              </EditButton>
              <DeleteButton 
                onClick={handleDeleteList}
                disabled={liking}
              >
                {liking ? 'Deleting...' : 'Delete List'}
              </DeleteButton>
            </>
          )}
        </div>
      </ActionsBar>

      {searchResults.length > 0 && (
        <SearchResults>
          {searchResults.map((album) => (
            <SearchResultItem key={album.discogs_id}>
              <AlbumCover 
                src={album.cover_image || album.thumb || '/static/music/default-album.svg'}
                alt={album.title}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/static/music/default-album.svg';
                }}
              />
              <AlbumInfo>
                <AlbumTitle>{album.title}</AlbumTitle>
                <AlbumArtist>{album.artist}</AlbumArtist>
                {album.year && <AlbumArtist>({album.year})</AlbumArtist>}
              </AlbumInfo>
              <AddButton
                onClick={() => handleAddAlbum(album)}
                disabled={addingAlbum.has(album.discogs_id) || albums.some(a => a.discogs_id === album.discogs_id)}
              >
                                  {addingAlbum.has(album.discogs_id) ? 'Adding...' : 
                   albums.some(a => a.discogs_id === album.discogs_id) ? 'Added' : 'Add'}
              </AddButton>
            </SearchResultItem>
          ))}
        </SearchResults>
      )}

      {albums.length === 0 ? (
        <EmptyState>
          <h3>No albums in this list</h3>
          <p>
            {isOwner 
              ? 'Search for albums above to add them to your list!'
              : 'This list is empty.'
            }
          </p>
        </EmptyState>
      ) : (
        <AlbumsGrid>
          {albums.map((album) => (
            <AlbumCard key={album.id} onClick={() => handleAlbumClick(album)}>
              <CardAlbumCover 
                src={album.cover_url || '/static/music/default-album.svg'}
                alt={album.title}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/static/music/default-album.svg';
                }}
              />
              <CardAlbumTitle>{album.title}</CardAlbumTitle>
              <CardAlbumArtist>{album.artist}</CardAlbumArtist>
              {album.year && <CardAlbumArtist>({album.year})</CardAlbumArtist>}
              
              {album.user_review_id && (
                <ReviewInfo>
                  ⭐ You reviewed this album
                </ReviewInfo>
              )}
              
              {isOwner && (
                <RemoveButton onClick={(e) => {
                  e.stopPropagation();
                  handleRemoveAlbum(album);
                }}>
                  Remove
                </RemoveButton>
              )}
            </AlbumCard>
          ))}
        </AlbumsGrid>
      )}
    </Container>
  );
};

export default ListDetailPage; 
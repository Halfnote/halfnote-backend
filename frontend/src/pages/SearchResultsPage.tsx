import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { musicAPI, userAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import FormattedTextEditor from '../components/FormattedTextEditor';

const Container = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
`;

const BackLink = styled.a`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  text-decoration: none;
  margin-bottom: 20px;
  transition: color 0.2s ease;
  cursor: pointer;

  &:hover {
    color: #111827;
  }
`;

const SearchHeader = styled.div`
  margin-bottom: 30px;
`;

const SearchQuery = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
`;

const SearchMeta = styled.p`
  color: #6b7280;
  font-size: 16px;
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

const ResultsSection = styled.div`
  margin-bottom: 40px;
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e5e7eb;
`;

const ResultItem = styled.div`
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  margin-bottom: 16px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  cursor: ${props => props.onClick ? 'pointer' : 'default'};

  &:hover {
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transform: translateY(-1px);
  }

  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
`;

const ResultImage = styled.img<{ $isUser?: boolean }>`
  width: 100px;
  height: 100px;
  border-radius: ${props => props.$isUser ? '50%' : '8px'};
  background: #e5e7eb;
  margin-right: 16px;
  object-fit: cover;
  flex-shrink: 0;

  @media (max-width: 768px) {
    margin-right: 0;
    margin-bottom: 12px;
  }
`;

const ResultInfo = styled.div`
  flex: 1;
`;

const ResultTitle = styled.h3`
  font-weight: 600;
  font-size: 18px;
  margin-bottom: 4px;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const VerifiedBadge = styled.span`
  color: #1d4ed8;
  font-size: 16px;
  display: inline-flex;
  align-items: center;
`;

const ResultSubtitle = styled.p`
  color: #6b7280;
  font-size: 16px;
  margin-bottom: 4px;
`;

const ResultMeta = styled.p`
  color: #9ca3af;
  font-size: 14px;
`;

const ResultActions = styled.div`
  display: flex;
  gap: 12px;
`;

const BtnPrimary = styled.button`
  background: #111827;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-block;

  &:hover {
    background: #374151;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const BtnSecondary = styled.button<{ $following?: boolean }>`
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-block;

  &:hover {
    background: #f9fafb;
  }

  &:disabled {
    background: #f3f4f6;
    color: #9ca3af;
    cursor: not-allowed;
  }
`;

const NoResults = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #9ca3af;

  h3 {
    font-size: 20px;
    margin-bottom: 8px;
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

// Modal styles (matching legacy modal design)
const Modal = styled.div<{ $visible: boolean }>`
  display: ${props => props.$visible ? 'flex' : 'none'};
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  z-index: 1000;
  align-items: center;
  justify-content: center;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 16px;
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
`;

const ModalHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
`;

const ModalTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: #111827;
`;

const ModalBody = styled.div`
  padding: 24px;
`;

const ModalFooter = styled.div`
  padding: 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  resize: vertical;
  min-height: 100px;

  &:focus {
    outline: none;
    border-color: #6366f1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  }
`;

const RatingContainer = styled.div`
  margin-bottom: 16px;
`;

const Slider = styled.input`
  width: 100%;
  -webkit-appearance: none;
  appearance: none;
  height: 8px;
  border-radius: 4px;
  background: #d1d5db;
  outline: none;
  margin: 12px 0;

  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #667eea;
    cursor: pointer;
    border: 2px solid white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }

  &::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #667eea;
    cursor: pointer;
    border: 2px solid white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }
`;

const RatingDisplay = styled.div`
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 8px;
`;

const RatingLabels = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
`;

const GenreGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
  margin-top: 12px;
`;

const GenreChip = styled.button<{ $selected: boolean }>`
  background: ${props => props.$selected ? '#111827' : 'white'};
  color: ${props => props.$selected ? 'white' : '#374151'};
  border: 1px solid ${props => props.$selected ? '#111827' : '#d1d5db'};
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.$selected ? '#374151' : '#f9fafb'};
  }
`;

interface SearchResult {
  id?: string;
  discogs_id?: string;
  title: string;
  artist: string;
  year?: number;
  cover_image?: string;
  thumb?: string;
  genres?: string[];
  styles?: string[];
}

interface UserResult {
  username: string;
  bio?: string;
  avatar?: string;
  is_following?: boolean;
  is_verified?: boolean;
}

const SearchResultsPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  
  const [albums, setAlbums] = useState<SearchResult[]>([]);
  const [users, setUsers] = useState<UserResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [followLoading, setFollowLoading] = useState<string>(''); // username currently being followed/unfollowed
  const [favoriteLoading, setFavoriteLoading] = useState<string>(''); // discogs_id currently being favorited/unfavorited
  const [userFavorites, setUserFavorites] = useState<string[]>([]); // user's favorite album discogs_ids
  
  // Review modal state
  const [reviewModalVisible, setReviewModalVisible] = useState(false);
  const [selectedAlbum, setSelectedAlbum] = useState<SearchResult | null>(null);
  const [reviewData, setReviewData] = useState({
    rating: 1,
    content: '',
    genres: [] as string[]
  });
  const [availableGenres, setAvailableGenres] = useState<Array<{ id: number; name: string }>>([]);
  const [reviewLoading, setReviewLoading] = useState(false);

  useEffect(() => {
    if (query) {
      performSearch();
      setAvailableGenres(COMMON_GENRES.map((name, index) => ({ id: index + 1, name })));
    }
  }, [query]);

  // Load user's favorite albums
  useEffect(() => {
    const loadUserFavorites = async () => {
      if (user) {
        try {
          const favorites = await userAPI.getFavoriteAlbums();
          setUserFavorites(favorites.favorite_albums?.map((album: any) => album.discogs_id) || []);
        } catch (error) {
          console.warn('Failed to load user favorites:', error);
        }
      }
    };
    loadUserFavorites();
  }, [user]);

  const performSearch = async () => {
    setLoading(true);
    setError('');
    try {
      // Search for albums
      const albumResults = await musicAPI.search(query);
      setAlbums(albumResults.results || []);

      // Search for users if authenticated
      if (user) {
        try {
          const userResults = await userAPI.searchUsers(query);
          setUsers(userResults.users || userResults || []);
        } catch (error) {
          console.warn('User search failed:', error);
          setUsers([]);
        }
      }
    } catch (error: any) {
      console.error('Error searching:', error);
      setError(error.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  // Hardcoded list of common music genres
  const COMMON_GENRES = [
    'Alternative',
    'Blues',
    'Classical',
    'Country',
    'Dance',
    'Electronic',
    'Folk',
    'Funk',
    'Hip-Hop',
    'House',
    'Indie',
    'Jazz',
    'Latin',
    'Metal',
    'Pop',
    'Punk',
    'R&B',
    'Rap',
    'Reggae',
    'Rock',
    'Soul',
    'Techno',
    'World'
  ];

  const openReviewModal = (album: SearchResult) => {
    if (!user) {
      navigate('/login');
      return;
    }
    setSelectedAlbum(album);
    setReviewData({
      rating: 5,
      content: '',
      genres: []
    });
    setReviewModalVisible(true);
  };

  const closeReviewModal = () => {
    setReviewModalVisible(false);
    setSelectedAlbum(null);
    setReviewData({ rating: 5, content: '', genres: [] });
  };

  const submitReview = async () => {
    if (!selectedAlbum || !user || reviewLoading) return;

    setReviewLoading(true);
    try {
      // Use discogs_id first, then fall back to id
      const albumId = selectedAlbum.discogs_id || selectedAlbum.id;
      if (!albumId) {
        throw new Error('No album ID found');
      }
      
      const newReview = await musicAPI.createReview(
        String(albumId),
        reviewData.rating,
        reviewData.content,
        reviewData.genres
      );
      
      closeReviewModal();
      // Navigate to the review detail page of the newly created review
      navigate(`/review/${newReview.id}/`);
    } catch (error: any) {
      console.error('Error submitting review:', error);
      setError(error.message || 'Failed to submit review');
    } finally {
      setReviewLoading(false);
    }
  };

  const followUser = async (username: string, shouldFollow: boolean) => {
    if (!user || followLoading === username) return;

    setFollowLoading(username);
    try {
      if (shouldFollow) {
        await userAPI.followUser(username);
      } else {
        await userAPI.unfollowUser(username);
      }
      
      // Update the user's follow status in the list
      setUsers(users.map(u => 
        u.username === username 
          ? { ...u, is_following: shouldFollow }
          : u
      ));
    } catch (error: any) {
      console.error('Error following/unfollowing user:', error);
      setError(error.message || 'Failed to update follow status');
    } finally {
      setFollowLoading('');
    }
  };

  const toggleGenre = (genreName: string) => {
    setReviewData(prev => ({
      ...prev,
      genres: prev.genres.includes(genreName)
        ? prev.genres.filter(g => g !== genreName)
        : [...prev.genres, genreName]
    }));
  };

  const toggleFavorite = async (album: SearchResult) => {
    if (!user || !album.discogs_id || favoriteLoading === album.discogs_id) return;

    setFavoriteLoading(album.discogs_id);
    try {
      const isFavorite = userFavorites.includes(album.discogs_id);
      
      if (isFavorite) {
        // Remove from favorites
        await userAPI.removeFavoriteAlbum(undefined, album.discogs_id);
        setUserFavorites(prev => prev.filter(id => id !== album.discogs_id));
      } else {
        // Add to favorites
        await userAPI.addFavoriteAlbum(undefined, album.discogs_id);
        setUserFavorites(prev => [...prev, album.discogs_id!]);
      }
    } catch (error: any) {
      console.error('Error toggling favorite:', error);
      setError(error.message || 'Failed to update favorite status');
    } finally {
      setFavoriteLoading('');
    }
  };

  // Remove star rendering function - now using slider

  const totalResults = albums.length + users.length;

  if (loading) {
    return (
      <Container>
        <LoadingDiv>
          <Spinner />
          <p>Searching...</p>
        </LoadingDiv>
      </Container>
    );
  }

  return (
    <Container>
      <BackLink onClick={() => navigate('/')}>
        ← Back to Home
      </BackLink>

      <SearchHeader>
        <SearchQuery>Search results for "{query}"</SearchQuery>
        <SearchMeta>Found {totalResults} results</SearchMeta>
      </SearchHeader>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      {users.length > 0 && (
        <ResultsSection>
          <SectionTitle>Users ({users.length})</SectionTitle>
          {users.map(userResult => (
            <ResultItem 
              key={userResult.username}
              onClick={() => navigate(`/users/${userResult.username}`)}
            >
              <ResultImage 
                $isUser
                src={userResult.avatar || '/static/accounts/default-avatar.svg'}
                alt={userResult.username}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/static/accounts/default-avatar.svg';
                }}
              />
              <ResultInfo>
                <ResultTitle>
                  {userResult.username}
                  {userResult.is_verified && <VerifiedBadge>✓</VerifiedBadge>}
                </ResultTitle>
                {userResult.bio && <ResultSubtitle>{userResult.bio}</ResultSubtitle>}
                <ResultMeta>User</ResultMeta>
              </ResultInfo>
              {user && user.username !== userResult.username && (
                <ResultActions onClick={(e) => e.stopPropagation()}>
                  {userResult.is_following ? (
                    <BtnSecondary 
                      $following 
                      onClick={() => followUser(userResult.username, false)}
                      disabled={followLoading === userResult.username}
                    >
                      {followLoading === userResult.username ? 'Updating...' : 'Following'}
                    </BtnSecondary>
                  ) : (
                    <BtnPrimary 
                      onClick={() => followUser(userResult.username, true)}
                      disabled={followLoading === userResult.username}
                    >
                      {followLoading === userResult.username ? 'Following...' : 'Follow'}
                    </BtnPrimary>
                  )}
                </ResultActions>
              )}
            </ResultItem>
          ))}
        </ResultsSection>
      )}

      {albums.length > 0 && (
        <ResultsSection>
          <SectionTitle>Albums ({albums.length})</SectionTitle>
          {albums.map(album => (
            <ResultItem key={album.discogs_id || album.id}>
              <ResultImage 
                src={album.cover_image || album.thumb || 'https://via.placeholder.com/100x100'}
                alt={album.title}
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://via.placeholder.com/100x100?text=No+Cover';
                }}
              />
              <ResultInfo>
                <ResultTitle>{album.title}</ResultTitle>
                <ResultSubtitle>{album.artist}</ResultSubtitle>
                <ResultMeta>
                  Album{album.year && ` • ${album.year}`}
                </ResultMeta>
              </ResultInfo>
              <ResultActions>
                <BtnPrimary onClick={() => openReviewModal(album)}>
                  {user ? 'Review' : 'Login to Review'}
                </BtnPrimary>
                {user && album.discogs_id && (
                  <BtnSecondary 
                    onClick={() => toggleFavorite(album)}
                    disabled={favoriteLoading === album.discogs_id}
                  >
                    {favoriteLoading === album.discogs_id 
                      ? 'Updating...' 
                      : userFavorites.includes(album.discogs_id) 
                        ? '⭐ Favorited' 
                        : '☆ Add to Favorites'
                    }
                  </BtnSecondary>
                )}
              </ResultActions>
            </ResultItem>
          ))}
        </ResultsSection>
      )}

      {totalResults === 0 && !loading && (
        <NoResults>
          <h3>No results found</h3>
          <p>Try searching with different keywords</p>
        </NoResults>
      )}

      {/* Review Modal */}
      <Modal $visible={reviewModalVisible} onClick={closeReviewModal}>
        <ModalContent onClick={(e) => e.stopPropagation()}>
          <ModalHeader>
            <ModalTitle>Review {selectedAlbum?.title}</ModalTitle>
          </ModalHeader>
          <ModalBody>
            <FormGroup>
              <Label>Rating</Label>
              <RatingContainer>
                <RatingDisplay>{reviewData.rating}/10</RatingDisplay>
                <Slider
                  type="range"
                  min="1"
                  max="10"
                  value={reviewData.rating}
                  onChange={(e) => setReviewData(prev => ({ 
                    ...prev, 
                    rating: parseInt(e.target.value) 
                  }))}
                />
                <RatingLabels>
                  <span>Terrible (1)</span>
                  <span>Masterpiece (10)</span>
                </RatingLabels>
              </RatingContainer>
            </FormGroup>
            
            <FormGroup>
              <Label>Review</Label>
              <FormattedTextEditor
                value={reviewData.content}
                onChange={(content) => setReviewData(prev => ({ ...prev, content }))}
                placeholder="Share your thoughts about this album..."
                minHeight="150px"
                disabled={reviewLoading}
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Genres (optional)</Label>
              <GenreGrid>
                {availableGenres.map(genre => (
                  <GenreChip
                    key={genre.id}
                    $selected={reviewData.genres.includes(genre.name)}
                    onClick={() => toggleGenre(genre.name)}
                  >
                    {genre.name}
                  </GenreChip>
                ))}
              </GenreGrid>
            </FormGroup>
          </ModalBody>
          <ModalFooter>
            <BtnSecondary onClick={closeReviewModal}>
              Cancel
            </BtnSecondary>
            <BtnPrimary 
              onClick={submitReview}
              disabled={reviewLoading || !reviewData.content.trim()}
            >
              {reviewLoading ? 'Submitting...' : 'Submit Review'}
            </BtnPrimary>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Container>
  );
};

export default SearchResultsPage;
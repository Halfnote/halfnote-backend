import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { musicAPI } from '../services/api';

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

const ArtistHeader = styled.div`
  display: flex;
  gap: 32px;
  margin-bottom: 40px;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
`;

const ArtistImage = styled.img`
  width: 200px;
  height: 200px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  background: #e5e7eb;
`;

const ArtistInfo = styled.div`
  flex: 1;
`;

const ArtistName = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
`;

const ArtistStats = styled.div`
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  color: #6b7280;
  font-size: 14px;

  @media (max-width: 768px) {
    justify-content: center;
  }
`;

const StatItem = styled.span`
  strong {
    color: #111827;
    font-weight: 600;
  }
`;

const ArtistBio = styled.p`
  color: #6b7280;
  font-size: 14px;
  line-height: 1.6;
  max-height: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e5e7eb;
`;

const AlbumGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
`;

const AlbumCard = styled.div`
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transform: translateY(-2px);
  }
`;

const AlbumCover = styled.img`
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  background: #e5e7eb;
`;

const AlbumDetails = styled.div`
  padding: 12px;
`;

const AlbumTitle = styled.h3`
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const AlbumMeta = styled.p`
  font-size: 12px;
  color: #6b7280;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const AlbumRating = styled.span`
  font-weight: 600;
  color: #6366f1;
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
  text-align: center;
`;

const NoResults = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #9ca3af;
`;

interface ArtistAlbum {
  id: string;
  title: string;
  artist: string;
  year?: number;
  cover_url?: string;
  discogs_id: string;
  avg_rating?: number;
  review_count: number;
}

interface ArtistData {
  name: string;
  image?: string;
  bio?: string;
  albums: ArtistAlbum[];
  album_count: number;
  average_rating?: number;
}

const ArtistPage: React.FC = () => {
  const { artistName } = useParams<{ artistName: string }>();
  const navigate = useNavigate();
  const [artist, setArtist] = useState<ArtistData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!artistName) return;

    const fetchArtist = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await musicAPI.getArtistDetail(artistName);
        setArtist(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load artist');
      } finally {
        setLoading(false);
      }
    };

    fetchArtist();
  }, [artistName]);

  if (loading) {
    return (
      <Container>
        <LoadingDiv>
          <Spinner />
          <p>Loading artist...</p>
        </LoadingDiv>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <BackLink onClick={() => navigate(-1)}>← Back</BackLink>
        <ErrorMessage>{error}</ErrorMessage>
      </Container>
    );
  }

  if (!artist) {
    return (
      <Container>
        <BackLink onClick={() => navigate(-1)}>← Back</BackLink>
        <NoResults>Artist not found</NoResults>
      </Container>
    );
  }

  return (
    <Container>
      <BackLink onClick={() => navigate(-1)}>← Back</BackLink>

      <ArtistHeader>
        {artist.image ? (
          <ArtistImage
            src={artist.image}
            alt={artist.name}
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
        ) : (
          <ArtistImage as="div" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '48px', color: '#9ca3af' }}>
            ♪
          </ArtistImage>
        )}
        <ArtistInfo>
          <ArtistName>{artist.name}</ArtistName>
          <ArtistStats>
            <StatItem><strong>{artist.album_count}</strong> album{artist.album_count !== 1 ? 's' : ''} reviewed</StatItem>
            {artist.average_rating && (
              <StatItem><strong>{artist.average_rating}</strong> avg rating</StatItem>
            )}
          </ArtistStats>
          {artist.bio && <ArtistBio>{artist.bio}</ArtistBio>}
        </ArtistInfo>
      </ArtistHeader>

      {artist.albums.length > 0 ? (
        <>
          <SectionTitle>Albums ({artist.album_count})</SectionTitle>
          <AlbumGrid>
            {artist.albums.map((album) => (
              <AlbumCard
                key={album.discogs_id}
                onClick={() => navigate(`/albums/${album.discogs_id}/`)}
              >
                <AlbumCover
                  src={album.cover_url || 'https://via.placeholder.com/200x200?text=No+Cover'}
                  alt={album.title}
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'https://via.placeholder.com/200x200?text=No+Cover';
                  }}
                />
                <AlbumDetails>
                  <AlbumTitle title={album.title}>{album.title}</AlbumTitle>
                  <AlbumMeta>
                    <span>{album.year || 'N/A'}</span>
                    <span>
                      {album.avg_rating ? (
                        <AlbumRating>{album.avg_rating}/10</AlbumRating>
                      ) : 'No ratings'}
                      {album.review_count > 0 && ` (${album.review_count})`}
                    </span>
                  </AlbumMeta>
                </AlbumDetails>
              </AlbumCard>
            ))}
          </AlbumGrid>
        </>
      ) : (
        <NoResults>
          <h3>No reviewed albums</h3>
          <p>No albums by {artist.name} have been reviewed yet.</p>
        </NoResults>
      )}
    </Container>
  );
};

export default ArtistPage;

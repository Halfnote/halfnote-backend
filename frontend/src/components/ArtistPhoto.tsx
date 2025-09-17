import React, { useState } from 'react';
import styled from 'styled-components';

interface ArtistPhotoProps {
  src?: string;
  alt?: string;
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

const sizeMap = {
  small: '60px',
  medium: '80px', 
  large: '150px'
};

const StyledArtistPhoto = styled.div<{ size: string }>`
  width: ${props => props.size};
  height: ${props => props.size};
  border-radius: 0;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ArtistImage = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
  
  &:hover {
    transform: scale(1.05);
  }
`;

const ArtistPlaceholder = styled.div`
  color: white;
  font-weight: bold;
  font-size: 0.8em;
  text-align: center;
  opacity: 0.8;
`;

const ArtistPhoto: React.FC<ArtistPhotoProps> = ({ 
  src, 
  alt = 'Artist photo', 
  size = 'medium',
  className 
}) => {
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

  const handleImageError = () => {
    setImageError(true);
    setImageLoading(false);
  };

  const handleImageLoad = () => {
    setImageLoading(false);
  };

  const shouldShowPlaceholder = !src || imageError;

  return (
    <StyledArtistPhoto size={sizeMap[size]} className={className}>
      {!shouldShowPlaceholder && (
        <ArtistImage
          src={src}
          alt={alt}
          onError={handleImageError}
          onLoad={handleImageLoad}
          style={{ 
            display: imageLoading ? 'none' : 'block'
          }}
        />
      )}
      {(shouldShowPlaceholder || imageLoading) && (
        <ArtistPlaceholder>
          🎤
        </ArtistPlaceholder>
      )}
    </StyledArtistPhoto>
  );
};

export default ArtistPhoto;
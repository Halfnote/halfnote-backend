import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { musicAPI } from '../services/api';
import FormattedTextEditor from './FormattedTextEditor';

interface Genre {
  id: number;
  name: string;
}

interface Review {
  id: number;
  rating: number;
  content: string;
  user_genres: Genre[];
}

interface EditReviewModalProps {
  isVisible: boolean;
  reviewId: number | null;
  onClose: () => void;
  onSave: () => void;
}

const Modal = styled.div<{ $visible: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: ${props => props.$visible ? 'flex' : 'none'};
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
`;

const ModalHeader = styled.div`
  margin-bottom: 20px;
`;

const ModalTitle = styled.h3`
  margin: 0;
  color: #111827;
  font-size: 18px;
  font-weight: 600;
`;

const FormGroup = styled.div`
  margin-bottom: 16px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
`;

const Input = styled.input`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-family: inherit;
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-family: inherit;
  min-height: 100px;
  resize: vertical;
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const GenreGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
`;

const GenreOption = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;

  input[type="checkbox"] {
    width: auto;
  }

  label {
    margin: 0;
    cursor: pointer;
    font-weight: normal;
  }
`;

const ModalFooter = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
`;

const Button = styled.button`
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
  border: none;
  font-family: inherit;
  transition: all 0.2s ease;
`;

const CancelButton = styled(Button)`
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;

  &:hover {
    background: #e5e7eb;
  }
`;

const SaveButton = styled(Button)`
  background: #667eea;
  color: white;

  &:hover {
    background: #5a67d8;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const EditReviewModal: React.FC<EditReviewModalProps> = ({
  isVisible,
  reviewId,
  onClose,
  onSave
}) => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [review, setReview] = useState<Review | null>(null);
  const [availableGenres, setAvailableGenres] = useState<Genre[]>([]);
  const [formData, setFormData] = useState({
    rating: 1,
    content: '',
    genres: [] as string[]
  });

  // Load review data when modal opens
  useEffect(() => {
    if (isVisible && reviewId) {
      loadReviewData();
      loadGenres();
    }
  }, [isVisible, reviewId]);

  const loadReviewData = async () => {
    if (!reviewId) return;
    
    setLoading(true);
    try {
      const reviewData = await musicAPI.getReview(reviewId);
      setReview(reviewData);
      setFormData({
        rating: reviewData.rating,
        content: reviewData.content,
        genres: reviewData.user_genres?.map((g: Genre) => g.name) || []
      });
    } catch (error) {
      console.error('Error loading review:', error);
      alert('Error loading review data');
      onClose();
    } finally {
      setLoading(false);
    }
  };

  const loadGenres = async () => {
    try {
      const genresData = await musicAPI.getGenres();
      setAvailableGenres(genresData.genres || genresData);
    } catch (error) {
      console.error('Error loading genres:', error);
    }
  };

  const handleGenreToggle = (genreName: string) => {
    setFormData(prev => ({
      ...prev,
      genres: prev.genres.includes(genreName)
        ? prev.genres.filter(g => g !== genreName)
        : [...prev.genres, genreName]
    }));
  };

  const handleSave = async () => {
    if (!reviewId || !formData.content.trim()) return;

    setSaving(true);
    try {
      await musicAPI.updateReview(
        reviewId, 
        formData.rating, 
        formData.content, 
        formData.genres
      );
      
      onSave(); // Callback to refresh the parent component
      onClose();
    } catch (error) {
      console.error('Error updating review:', error);
      alert('Error updating review');
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    if (!saving) {
      onClose();
    }
  };

  if (!isVisible) return null;

  return (
    <Modal $visible={isVisible} onClick={handleClose}>
      <ModalContent onClick={(e) => e.stopPropagation()}>
        <ModalHeader>
          <ModalTitle>Edit Review</ModalTitle>
        </ModalHeader>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            Loading review data...
          </div>
        ) : (
          <>
            <FormGroup>
              <Label htmlFor="edit-rating">Rating (1-10)</Label>
              <Input
                id="edit-rating"
                type="number"
                min="1"
                max="10"
                value={formData.rating}
                onChange={(e) => {
                  const value = parseInt(e.target.value) || 1;
                  const clampedValue = Math.max(1, Math.min(10, value)); // Clamp between 1-10
                  setFormData(prev => ({ 
                    ...prev, 
                    rating: clampedValue 
                  }));
                }}
                required
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="edit-content">Review</Label>
              <FormattedTextEditor
                value={formData.content}
                onChange={(content) => setFormData(prev => ({ 
                  ...prev, 
                  content 
                }))}
                placeholder="Share your thoughts about this album..."
                minHeight="150px"
                disabled={saving}
              />
            </FormGroup>

            <FormGroup>
              <Label>Genres</Label>
              <GenreGrid>
                {availableGenres.map(genre => (
                  <GenreOption key={genre.id}>
                    <input
                      type="checkbox"
                      id={`edit-genre-${genre.id}`}
                      checked={formData.genres.includes(genre.name)}
                      onChange={() => handleGenreToggle(genre.name)}
                    />
                    <label htmlFor={`edit-genre-${genre.id}`}>
                      {genre.name}
                    </label>
                  </GenreOption>
                ))}
              </GenreGrid>
            </FormGroup>
          </>
        )}

        <ModalFooter>
          <CancelButton onClick={handleClose} disabled={saving}>
            Cancel
          </CancelButton>
          <SaveButton 
            onClick={handleSave} 
            disabled={loading || saving || !formData.content.trim()}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </SaveButton>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default EditReviewModal; 
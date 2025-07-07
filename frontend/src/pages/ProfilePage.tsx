import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';
import { userAPI, musicAPI } from '../services/api';
import EditReviewModal from '../components/EditReviewModal';
import { renderFormattedText } from '../utils/textFormatting';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
`;

const BackLink = styled.button`
  background: none;
  border: none;
  color: #6b7280;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;

  &:hover {
    color: #111827;
  }
`;

const ProfileHeader = styled.div`
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: relative;

  @media (max-width: 768px) {
    text-align: center;
    padding: 24px;
  }
`;

const ProfileInfo = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 24px;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
`;

const ProfileTopRight = styled.div`
  position: absolute;
  top: 32px;
  right: 32px;
  display: flex;
  align-items: center;
  gap: 16px;

  @media (max-width: 768px) {
    position: static;
    margin-top: 16px;
    flex-direction: column;
  }
`;

const ProfileAllStats = styled.div`
  display: flex;
  gap: 32px;
  margin-bottom: 16px;
  align-items: center;
`;

const ProfileAvatar = styled.img`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s ease;

  @media (max-width: 768px) {
    margin: 0 auto;
  }

  &:hover {
    transform: scale(1.05);
  }
`;

const ProfileDetails = styled.div`
  flex: 1;
`;

const ProfileName = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
`;

const ProfileBio = styled.p`
  color: #6b7280;
  font-size: 16px;
  margin-bottom: 16px;
  white-space: pre-wrap;
`;

const ProfileStats = styled.div`
  display: flex;
  gap: 32px;
  margin-bottom: 16px;
  align-items: center;

  @media (max-width: 768px) {
    gap: 16px;
  }
`;

const Stat = styled.div`
  text-align: center;
  min-width: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const StatLink = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: none;
  color: inherit;
  transition: color 0.2s ease;
  text-align: center;
  min-width: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0;

  &:hover {
    color: #667eea;
  }
`;

const StatNumber = styled.span`
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  line-height: 1.2;
  margin-bottom: 4px;
`;

const StatLabel = styled.span`
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
  line-height: 1;
`;

const FollowButton = styled.button<{ $isFollowing?: boolean }>`
  background: ${props => props.$isFollowing ? 'white' : '#111827'};
  color: ${props => props.$isFollowing ? '#374151' : 'white'};
  border: ${props => props.$isFollowing ? '1px solid #d1d5db' : 'none'};
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.$isFollowing ? '#fee2e2' : '#374151'};
    color: ${props => props.$isFollowing ? '#dc2626' : 'white'};
    border-color: ${props => props.$isFollowing ? '#fca5a5' : 'transparent'};
  }
`;

const EditProfileButton = styled.button`
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;

  &:hover {
    background: #f9fafb;
  }
`;

const GenreSection = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const GenreSectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 16px;
`;

const GenreStatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
`;

const GenreStatItem = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  border: 1px solid #e9ecef;
`;

const GenreStatName = styled.div`
  font-size: 14px;
  font-weight: 500;
  color: #495057;
  margin-bottom: 4px;
`;

const GenreStatCount = styled.div`
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
`;

const EmptyGenreMessage = styled.div`
  text-align: center;
  color: #9ca3af;
  font-style: italic;
  padding: 20px;
`;

const GenresList = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
`;

const GenreTag = styled.span`
  background: #f3f4f6;
  color: #374151;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
`;

const FavoriteAlbumsSection = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const FavoriteAlbumsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;

  @media (max-width: 1200px) {
    grid-template-columns: repeat(3, 1fr);
  }

  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
`;

const FavoriteAlbumItem = styled.div`
  position: relative;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #e9ecef;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`;

const FavoriteAlbumCover = styled.img`
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  object-fit: cover;
  margin-bottom: 12px;
`;

const FavoriteAlbumInfo = styled.div`
  text-align: center;
`;

const FavoriteAlbumTitle = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
  line-height: 1.3;
`;

const FavoriteAlbumArtist = styled.div`
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 6px;
`;

const FavoriteAlbumRating = styled.div`
  font-size: 12px;
  color: #f59e0b;
  font-weight: 500;
`;

const RemoveFavoriteButton = styled.button`
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(220, 38, 38, 0.9);
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;

  ${FavoriteAlbumItem}:hover & {
    opacity: 1;
  }

  &:hover {
    background: #dc2626;
  }
`;

const TabsContainer = styled.div`
  background: white;
  border-radius: 16px;
  padding: 0;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const TabsList = styled.div`
  display: flex;
  border-bottom: 1px solid #e5e7eb;
`;

const Tab = styled.button<{ $active?: boolean }>`
  background: ${props => props.$active ? '#111827' : 'transparent'};
  color: ${props => props.$active ? 'white' : '#6b7280'};
  border: none;
  padding: 16px 24px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 0;

  &:hover {
    background: ${props => props.$active ? '#111827' : '#f9fafb'};
    color: ${props => props.$active ? 'white' : '#111827'};
  }
`;

const TabContent = styled.div`
  padding: 32px;
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

const ActivityReviewContent = styled.div`
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

const ActivityCommentContent = styled.div`
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

const ActivityAlbumCover = styled.img`
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

const NoActivity = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;

  h3 {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #374151;
  }

  p {
    font-size: 14px;
    line-height: 1.5;
  }
`;

const ReviewsSection = styled.div`
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 24px;
`;

const ReviewItem = styled.div`
  display: flex;
  gap: 16px;
  padding: 20px 0;
  border-bottom: 1px solid #f3f4f6;
  position: relative;

  &:last-child {
    border-bottom: none;
  }
`;

const ReviewAlbumCover = styled.img`
  width: 120px;
  height: 120px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
`;

const ReviewContentWrapper = styled.div`
  flex: 1;
`;

const ReviewHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
`;

const ReviewHeaderRight = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ReviewAlbumTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
`;

const ReviewTitleLink = styled.button`
  background: none;
  border: none;
  color: #111827;
  text-decoration: none;
  transition: color 0.2s ease;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  text-align: left;
  padding: 0;

  &:hover {
    color: #667eea;
    text-decoration: underline;
  }
`;

const ReviewAlbumArtist = styled.p`
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
`;

const ReviewRating = styled.span`
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
`;

const ReviewRatingSection = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
`;

const ReviewEngagement = styled.div`
  font-size: 11px;
  color: #9ca3af;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const ReviewBottomActions = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
`;

const ReviewEngagementActions = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 12px;
  color: #6b7280;
`;

const EngagementButton = styled.button<{ $active?: boolean }>`
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  color: ${props => props.$active ? '#ef4444' : '#6b7280'};
  transition: color 0.2s ease;
  padding: 4px;
  border-radius: 4px;
  
  &:hover:not(:disabled) {
    color: ${props => props.$active ? '#dc2626' : '#374151'};
    background: #f9fafb;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ReviewContent = styled.p`
  color: #374151;
  line-height: 1.5;
  margin-bottom: 8px;
`;

const ReviewMeta = styled.div`
  font-size: 12px;
  color: #9ca3af;
`;

const ReviewUserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
`;

const ReviewUserAvatar = styled.img`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
`;

const ReviewUsername = styled.span`
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
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

const SuccessMessage = styled.div`
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
  padding: 16px;
  border-radius: 8px;
  margin: 16px 0;
  text-align: center;
`;

const NoReviews = styled.div`
  text-align: center;
  color: #6b7280;
  padding: 40px 20px;
  font-style: italic;
`;

const EditProfileModal = styled.div<{ $visible: boolean }>`
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
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const ModalTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: #111827;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    color: #111827;
  }
`;

const FormGroup = styled.div`
  margin-bottom: 16px;
`;

const Label = styled.label`
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
`;

const Input = styled.input`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const SaveButton = styled.button`
  background: #111827;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s ease;

  &:hover {
    background: #374151;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const FileUploadSection = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
`;

const FileUploadContainer = styled.div`
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  
  &:hover {
    border-color: #667eea;
    background: #f9fafb;
  }
`;

const FileUploadLabel = styled.label`
  display: block;
  cursor: pointer;
  color: #374151;
  font-weight: 500;
  margin-bottom: 8px;
  font-size: 16px;
`;

const FileUploadHint = styled.p`
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 16px;
`;

const FileUploadButton = styled.button`
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #5a6fd8;
  }
`;

const HiddenFileInput = styled.input`
  position: absolute;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
`;

const ImagePreview = styled.div`
  margin-top: 16px;
  position: relative;
`;

const AvatarPreviewContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 16px;
`;

const AvatarPreviewImage = styled.img`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #e5e7eb;
`;

const BannerPreviewContainer = styled.div`
  margin-top: 16px;
`;

const BannerPreviewImage = styled.img`
  width: 100%;
  height: 120px;
  border-radius: 8px;
  object-fit: cover;
  border: 2px solid #e5e7eb;
`;

const PreviewLabel = styled.p`
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
  font-weight: 500;
`;

const RemoveButton = styled.button`
  background: #ef4444;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s ease;
  margin-top: 8px;
  
  &:hover {
    background: #dc2626;
  }
`;

const ReviewActions = styled.div`
  display: flex;
  gap: 4px;
  margin-top: 8px;
`;

const ActionButton = styled.button<{ $pinned?: boolean }>`
  background: ${props => props.$pinned ? '#fef3c7' : '#f3f4f6'};
  border: ${props => props.$pinned ? '1px solid #f59e0b' : 'none'};
  color: ${props => props.$pinned ? '#92400e' : '#6b7280'};
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: ${props => props.$pinned ? '#fde68a' : '#e5e7eb'};
    color: #374151;
  }
`;

const LikeButton = styled.button<{ $liked?: boolean }>`
  background: none;
  border: none;
  cursor: pointer;
  color: ${props => props.$liked ? '#dc2626' : '#6b7280'};
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;

  &:hover {
    color: ${props => props.$liked ? '#b91c1c' : '#374151'};
  }
`;

const LikesModal = styled.div<{ $visible: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: ${props => props.$visible ? 'flex' : 'none'};
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const LikesModalContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
  max-height: 500px;
  overflow-y: auto;
`;

const LikesModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
`;

const LikesModalTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0;
`;

const LikeUserItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;

  &:last-child {
    border-bottom: none;
  }
`;

const LikeUserAvatar = styled.img`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
`;

const LikeUserName = styled.span`
  font-weight: 500;
  color: #111827;
`;

const GenreGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
`;

const GenreOption = styled.label`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s ease;

  &:hover {
    background: #f3f4f6;
  }

  input[type="checkbox"] {
    margin: 0;
  }
`;



const ProfileBanner = styled.div<{ $backgroundImage?: string }>`
  width: 100%;
  height: 200px;
  background: ${props => props.$backgroundImage 
    ? `linear-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.1)), url(${props.$backgroundImage})`
    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  };
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  border-radius: 12px;
  position: relative;
  margin-bottom: 20px;
  cursor: ${props => props.onClick ? 'pointer' : 'default'};
  transition: opacity 0.2s;
  
  &:hover {
    opacity: ${props => props.onClick ? '0.9' : '1'};
  }
`;

const BannerOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  
  ${ProfileBanner}:hover & {
    opacity: 1;
  }
`;

const BannerEditText = styled.div`
  color: white;
  font-size: 16px;
  font-weight: 500;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
`;



interface User {
  id: number;
  username: string;
  name?: string;
  display_name: string;
  bio?: string;
  location?: string;
  avatar?: string;
  banner?: string;
  follower_count: number;
  following_count: number;
  review_count: number;
  favorite_genres: Array<{ id: number; name: string }>;
  favorite_albums?: Array<{
    id: string;
    title: string;
    artist: string;
    year?: number;
    cover_url?: string;
    discogs_id: string;
    user_review_id?: number;
    user_rating?: number;
    user_review_content?: string;
  }>;
  most_reviewed_genres?: Array<{ id: number; name: string; count: number }>;
  is_following?: boolean;
  is_staff?: boolean;
  is_verified?: boolean;
}

interface Review {
  id: number;
  username: string;
  user_avatar?: string;
  album_title: string;
  album_artist: string;
  album_cover?: string;
  album_year?: number;
  album_discogs_id?: string;
  rating: number;
  content: string;
  created_at: string;
  is_pinned: boolean;
  likes_count: number;
  comments_count: number;
  is_liked_by_user: boolean;
  user_genres?: Array<{ id: number; name: string }>;
}

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
    likes_count?: number;
    is_liked_by_user?: boolean;
    comments_count?: number;
    user_genres: Array<{ id: number; name: string }>;
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

const ProfilePage: React.FC = () => {
  const { username } = useParams<{ username: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [profileUser, setProfileUser] = useState<User | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'reviews' | 'activity' | 'lists'>('reviews');
  
  // Edit profile modal state
  const [showEditModal, setShowEditModal] = useState(false);
  const [editBio, setEditBio] = useState('');
  const [editName, setEditName] = useState('');
  const [editLocation, setEditLocation] = useState('');
  const [editFavoriteGenres, setEditFavoriteGenres] = useState<string[]>([]);
  const [editAvatar, setEditAvatar] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string>('');
  const [editBanner, setEditBanner] = useState<File | null>(null);
  const [bannerPreview, setBannerPreview] = useState<string>('');
  const [availableGenres, setAvailableGenres] = useState<Array<{ id: number; name: string }>>([]);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState<string>('');
  const [profileError, setProfileError] = useState<string>('');
  
  // Likes modal state
  const [showLikesModal, setShowLikesModal] = useState(false);
  const [likesData, setLikesData] = useState<{ users: Array<{ id: number; username: string; avatar?: string }> } | null>(null);
  const [loadingLikes, setLoadingLikes] = useState(false);
  
  // Edit review modal state
  const [showEditReviewModal, setShowEditReviewModal] = useState(false);
  const [editingReviewId, setEditingReviewId] = useState<number | null>(null);
  const [likingReviews, setLikingReviews] = useState<Set<number>>(new Set()); // Track which reviews are being liked
  
  // Activity feed state
  const [activities, setActivities] = useState<Activity[]>([]);
  const [activitiesLoading, setActivitiesLoading] = useState(false);
  
  // Lists state
  const [lists, setLists] = useState<any[]>([]);
  const [listsLoading, setListsLoading] = useState(false);
  
  // Create list modal state
  const [showCreateListModal, setShowCreateListModal] = useState(false);
  const [createListName, setCreateListName] = useState('');
  const [createListDescription, setCreateListDescription] = useState('');
  const [creatingList, setCreatingList] = useState(false);

  const isOwnProfile = user?.username === username;
  const pinnedReviews = reviews.filter(review => review.is_pinned);

  const loadProfile = useCallback(async () => {
    if (!username) return;
    
    try {
      const userData = await userAPI.getProfile(username);
      setProfileUser(userData);
      
      // Initialize edit form with current data
      if (isOwnProfile) {
        setEditBio(userData.bio || '');
        setEditName(userData.name || '');
        setEditLocation(userData.location || '');
        setEditFavoriteGenres(
          userData.favorite_genres?.map((g: any) => 
            typeof g === 'string' ? g : g.name
          ) || []
        );
        setAvatarPreview(userData.avatar || '');
        setBannerPreview(userData.banner || '');
      }
    } catch (err: any) {
      console.error('Failed to load profile:', err);
      throw err; // Re-throw to be caught by loadData
    }
  }, [username, isOwnProfile]);

  const loadReviews = useCallback(async () => {
    if (!username) return;
    
    try {
      const reviewsData = await userAPI.getUserReviews(username);
      // Sort reviews by creation date (newest first - LIFO)
      const sortedReviews = reviewsData.sort((a: Review, b: Review) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setReviews(sortedReviews);
    } catch (err: any) {
      console.error('Failed to load reviews:', err);
    }
  }, [username]);

  const loadActivities = useCallback(async () => {
    if (!username) return;
    
    setActivitiesLoading(true);
    try {
      const response = await fetch(`/api/accounts/users/${username}/activity/`, {
        headers: {
          'Authorization': user ? `Bearer ${localStorage.getItem('access_token')}` : '',
        },
      });
      
      if (response.ok) {
        const activitiesData = await response.json();
        setActivities(activitiesData);
      }
    } catch (err: any) {
      console.error('Failed to load activities:', err);
    } finally {
      setActivitiesLoading(false);
    }
  }, [username, user]);

  const loadLists = useCallback(async () => {
    if (!username) return;
    
    setListsLoading(true);
    try {
      const response = await fetch(`/api/music/users/${username}/lists/`, {
        headers: {
          'Authorization': user ? `Bearer ${localStorage.getItem('access_token')}` : '',
        },
      });
      
      if (response.ok) {
        const listsData = await response.json();
        setLists(listsData);
      }
    } catch (err: any) {
      console.error('Failed to load lists:', err);
    } finally {
      setListsLoading(false);
    }
  }, [username, user]);

  const handleCreateList = async () => {
    if (!createListName.trim()) return;
    
    setCreatingList(true);
    setProfileError(''); // Clear any previous errors
    setSuccess(''); // Clear any previous success messages
    try {
      const response = await fetch('/api/music/lists/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          name: createListName.trim(),
          description: createListDescription.trim() || undefined, // Use undefined instead of null for optional field
        }),
      });

      if (response.ok) {
        const newList = await response.json();
        setLists(prev => [newList, ...prev]);
        setShowCreateListModal(false);
        setCreateListName('');
        setCreateListDescription('');
        setSuccess('List created successfully!');
        setTimeout(() => setSuccess(''), 3000);
        
        // Navigate to the newly created list
        navigate(`/lists/${newList.id}`);
      } else {
        const errorData = await response.json();
        // Handle both types of error responses
        let errorMessage = 'Failed to create list';
        if (errorData.error) {
          errorMessage = errorData.error;
        } else if (errorData.name && errorData.name[0]) {
          errorMessage = `Name: ${errorData.name[0]}`;
        } else if (typeof errorData === 'object') {
          // Handle other field-specific errors
          const firstField = Object.keys(errorData)[0];
          if (firstField && errorData[firstField] && errorData[firstField][0]) {
            errorMessage = `${firstField}: ${errorData[firstField][0]}`;
          }
        }
        setProfileError(errorMessage);
        setTimeout(() => setProfileError(''), 5000);
      }
    } catch (err: any) {
      console.error('Failed to create list:', err);
      setProfileError('Failed to create list');
      setTimeout(() => setProfileError(''), 5000);
    } finally {
      setCreatingList(false);
    }
  };

  const loadData = useCallback(async () => {
    if (!username) return;
    
    setLoading(true);
    setError('');
    setProfileUser(null);
    
    try {
      // Load both profile and reviews in parallel
      await Promise.all([
        loadProfile(),
        loadReviews()
      ]);
    } catch (err: any) {
      console.error('Failed to load data:', err);
      setError(err.message || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  }, [username, loadProfile, loadReviews]);

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

  const handleFollow = async () => {
    if (!profileUser || !user) return;
    
    try {
      if (profileUser.is_following) {
        await userAPI.unfollowUser(profileUser.username);
        setProfileUser({
          ...profileUser,
          is_following: false,
          follower_count: profileUser.follower_count - 1
        });
      } else {
        await userAPI.followUser(profileUser.username);
        setProfileUser({
          ...profileUser,
          is_following: true,
          follower_count: profileUser.follower_count + 1
        });
      }
    } catch (error) {
      console.error('Error following/unfollowing user:', error);
    }
  };

  const handleEditProfile = () => {
    setAvailableGenres(COMMON_GENRES.map((name, index) => ({ id: index + 1, name })));
    setSuccess('');
    setProfileError('');
    setShowEditModal(true);
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setEditAvatar(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setAvatarPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleBannerChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setEditBanner(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setBannerPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveAvatar = () => {
    setEditAvatar(null);
    setAvatarPreview(profileUser?.avatar || '');
  };

  const handleRemoveBanner = () => {
    setEditBanner(null);
    setBannerPreview(profileUser?.banner || '');
  };

  const handleAvatarButtonClick = () => {
    const fileInput = document.getElementById('avatar-input') as HTMLInputElement;
    fileInput?.click();
  };

  const handleBannerButtonClick = () => {
    const fileInput = document.getElementById('banner-input') as HTMLInputElement;
    fileInput?.click();
  };

  const handleGenreToggle = (genreName: string) => {
    setEditFavoriteGenres(prev => 
      prev.includes(genreName)
        ? prev.filter(g => g !== genreName)
        : [...prev, genreName]
    );
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    
    try {
      const formData = new FormData();
      
      formData.append('bio', editBio.trim());
      formData.append('name', editName.trim());
      formData.append('location', editLocation.trim());
      formData.append('favorite_genres', JSON.stringify(editFavoriteGenres));
      
      if (editAvatar) {
        formData.append('avatar', editAvatar);
      }
      
      if (editBanner) {
        formData.append('banner', editBanner);
      }

      const updatedUser = await userAPI.updateProfile(formData);
      
      // Update the profile user state immediately with the response data
      setProfileUser(updatedUser);
      
      // Update avatar preview if a new avatar was uploaded
      if (editAvatar && updatedUser.avatar) {
        setAvatarPreview(updatedUser.avatar);
      }
      
      // Update banner preview if a new banner was uploaded
      if (editBanner && updatedUser.banner) {
        setBannerPreview(updatedUser.banner);
      }
      
      // Clear the edit files since they're now saved
      setEditAvatar(null);
      setEditBanner(null);
      
      setShowEditModal(false);
      
      // Reload the profile data to ensure everything is fresh and consistent
      await loadProfile();
      
      // Modern UX: Show success without requiring user action
      setSuccess('Profile updated successfully!');
      setTimeout(() => setSuccess(''), 3000); // Auto-hide after 3 seconds
    } catch (error: any) {
      console.error('Error updating profile:', error);
      console.error('Full error response:', error.response?.data);
      
      // Show detailed error for debugging
      if (error.response?.data) {
        const errorData = error.response.data;
        let errorMessage = errorData.error || 'Unknown error';
        
        // Add debug information if available
        if (errorData.debug_info) {
          errorMessage += `\n\nDebug Info:\n- Type: ${errorData.error_type}\n- Exception: ${errorData.debug_info.exception_str}`;
        }
        
        if (errorData.traceback) {
          console.error('Server traceback:', errorData.traceback);
        }
        
        setProfileError(errorMessage);
      } else {
        setProfileError('Failed to update profile: ' + (error.message || 'Unknown error'));
      }
      setTimeout(() => setProfileError(''), 15000); // Longer timeout for debugging
    } finally {
      setSaving(false);
    }
  };

  const getTimeAgo = (dateString: string) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      const days = Math.floor(diff / 86400000);
      const hours = Math.floor(diff / 3600000);
      const minutes = Math.floor(diff / 60000);

      if (days > 0) return `${days}d ago`;
      if (hours > 0) return `${hours}h ago`;
      return `${minutes}m ago`;
    } catch (error) {
      return 'Unknown time';
    }
  };

  const handlePinReview = async (reviewId: number, currentlyPinned: boolean) => {
    if (!user || !isOwnProfile) return;
    
    try {
      await musicAPI.pinReview(reviewId);
      
      // Reload both reviews and profile to get updated pin status and pinned reviews section
      loadReviews();
      loadProfile(); // This updates the pinned_reviews in profileUser
    } catch (error: any) {
      console.error('Error toggling pin:', error);
      // Display the actual error message from the backend
      const errorMessage = error.response?.data?.error || error.message || 'Error updating pin status';
      alert(errorMessage);
    }
  };

  const handleEditReview = (reviewId: number) => {
    setEditingReviewId(reviewId);
    setShowEditReviewModal(true);
  };

  const handleCloseEditReviewModal = () => {
    setShowEditReviewModal(false);
    setEditingReviewId(null);
  };

  const handleSaveEditReview = () => {
    // Reload reviews to show the updated review
    loadReviews();
    loadProfile(); // Also reload profile to update review count if needed
  };

  const handleDeleteReview = async (reviewId: number) => {
    if (!user || !isOwnProfile) return;
    
    if (!window.confirm('Are you sure you want to delete this review?')) return;
    
    try {
      await musicAPI.deleteReview(reviewId);
      
      // Reload reviews to remove deleted review
      loadReviews();
      loadProfile(); // Update review count
    } catch (error: any) {
      console.error('Error deleting review:', error);
      alert('Error deleting review');
    }
  };

  const handleLikeReview = async (reviewId: number, currentlyLiked: boolean) => {
    if (!user || likingReviews.has(reviewId)) return; // Prevent double-clicks
    
    setLikingReviews(prev => new Set(prev).add(reviewId));
    try {
      await musicAPI.likeReview(reviewId);
      
      // Update the review in both pinned and regular reviews
      const updateReview = (review: Review) => {
        if (review.id === reviewId) {
          return {
            ...review,
            is_liked_by_user: !currentlyLiked,
            likes_count: currentlyLiked ? review.likes_count - 1 : review.likes_count + 1
          };
        }
        return review;
      };
      
      setReviews(prev => prev.map(updateReview));
    } catch (error: any) {
      console.error('Error toggling like:', error);
      alert('Error updating like status');
    } finally {
      setLikingReviews(prev => {
        const newSet = new Set(prev);
        newSet.delete(reviewId);
        return newSet;
      });
    }
  };

  const handleShowLikes = async (reviewId: number) => {
    navigate(`/review/${reviewId}/likes`);
  };

  const handleRemoveFavoriteAlbum = async (albumId: string) => {
    if (!user || !isOwnProfile) return;
    
    try {
      await userAPI.removeFavoriteAlbum(albumId);
      
      // Reload profile to update favorite albums
      await loadProfile();
      
      setSuccess('Album removed from favorites!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (error: any) {
      console.error('Error removing favorite album:', error);
      setProfileError('Failed to remove album from favorites');
      setTimeout(() => setProfileError(''), 5000);
    }
  };

  const formatActivityTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    return date.toLocaleDateString();
  };

  const renderActivityText = (activity: Activity) => {
    try {
      const isCurrentUser = activity.user.username === user?.username;
      const isTargetCurrentUser = activity.target_user?.username === user?.username;

      switch (activity.activity_type) {
        case 'review_created':
          return (
            <>
              {isCurrentUser ? (
                <span style={{ fontWeight: 600, color: '#111827' }}>You</span>
              ) : (
                <>
                  <ActivityUser onClick={() => navigate(`/users/${activity.user.username}`)}>
                    {activity.user.username}
                  </ActivityUser>
                  {activity.user.is_staff && (
                    <span 
                      style={{ 
                        marginLeft: '4px', 
                        fontSize: '14px',
                        color: '#3b82f6',
                        fontWeight: 'bold'
                      }}
                      title="Verified Staff"
                    >
                      ✓
                    </span>
                  )}
                </>
              )}
              {' reviewed '}
              <ActivityAlbum onClick={() => navigate(`/review/${activity.review_details?.id}/`)}>
                {activity.review_details?.album?.title || 'an album'}
              </ActivityAlbum>
            </>
          );
        case 'user_followed':
          return (
            <>
              {isCurrentUser ? (
                <span style={{ fontWeight: 600, color: '#111827' }}>You</span>
              ) : (
                <>
                  <ActivityUser onClick={() => navigate(`/users/${activity.user.username}`)}>
                    {activity.user.username}
                  </ActivityUser>
                  {activity.user.is_staff && (
                    <span 
                      style={{ 
                        marginLeft: '4px', 
                        fontSize: '14px',
                        color: '#3b82f6',
                        fontWeight: 'bold'
                      }}
                      title="Verified Staff"
                    >
                      ✓
                    </span>
                  )}
                </>
              )}
              {' followed '}
              {isTargetCurrentUser ? (
                <span style={{ fontWeight: 600, color: '#111827' }}>you</span>
              ) : (
                <>
                  <ActivityUser onClick={() => navigate(`/users/${activity.target_user?.username}`)}>
                    {activity.target_user?.username}
                  </ActivityUser>
                  {activity.target_user?.is_staff && (
                    <span 
                      style={{ 
                        marginLeft: '4px', 
                        fontSize: '14px',
                        color: '#3b82f6',
                        fontWeight: 'bold'
                      }}
                      title="Verified Staff"
                    >
                      ✓
                    </span>
                  )}
                </>
              )}
            </>
          );
        case 'review_liked':
          return (
            <>
              {isCurrentUser ? (
                <span style={{ fontWeight: 600, color: '#111827' }}>You</span>
              ) : (
                <>
                  <ActivityUser onClick={() => navigate(`/users/${activity.user.username}`)}>
                    {activity.user.username}
                  </ActivityUser>
                  {activity.user.is_staff && (
                    <span 
                      style={{ 
                        marginLeft: '4px', 
                        fontSize: '14px',
                        color: '#3b82f6',
                        fontWeight: 'bold'
                      }}
                      title="Verified Staff"
                    >
                      ✓
                    </span>
                  )}
                </>
              )}
              {' liked '}
              {activity.review_details?.user?.username === user?.username ? (
                <span style={{ fontWeight: 600, color: '#111827' }}>your</span>
              ) : (
                <>
                  <ActivityUser onClick={() => navigate(`/users/${activity.review_details?.user?.username}`)}>
                    {activity.review_details?.user?.username}
                  </ActivityUser>
                  {activity.review_details?.user?.is_staff && (
                    <span 
                      style={{ 
                        marginLeft: '4px', 
                        fontSize: '14px',
                        color: '#3b82f6',
                        fontWeight: 'bold'
                      }}
                      title="Verified Staff"
                    >
                      ✓
                    </span>
                  )}
                  <span>'s</span>
                </>
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
                <>
                  <ActivityUser onClick={() => navigate(`/users/${activity.user.username}`)}>
                    {activity.user.username}
                  </ActivityUser>
                  {activity.user.is_staff && (
                    <span 
                      style={{ 
                        marginLeft: '4px', 
                        fontSize: '14px',
                        color: '#3b82f6',
                        fontWeight: 'bold'
                      }}
                      title="Verified Staff"
                    >
                      ✓
                    </span>
                  )}
                </>
              )}
              {' commented on '}
              {activity.review_details?.user?.username === user?.username ? (
                <span style={{ fontWeight: 600, color: '#111827' }}>your</span>
              ) : (
                <>
                  <ActivityUser onClick={() => navigate(`/users/${activity.review_details?.user?.username}`)}>
                    {activity.review_details?.user?.username}
                  </ActivityUser>
                  {activity.review_details?.user?.is_staff && (
                    <span 
                      style={{ 
                        marginLeft: '4px', 
                        fontSize: '14px',
                        color: '#3b82f6',
                        fontWeight: 'bold'
                      }}
                      title="Verified Staff"
                    >
                      ✓
                    </span>
                  )}
                  <span>'s</span>
                </>
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
                <>
                  <ActivityUser onClick={() => navigate(`/users/${activity.user.username}`)}>
                    {activity.user.username}
                  </ActivityUser>
                  {activity.user.is_staff && (
                    <span 
                      style={{ 
                        marginLeft: '4px', 
                        fontSize: '14px',
                        color: '#3b82f6',
                        fontWeight: 'bold'
                      }}
                      title="Verified Staff"
                    >
                      ✓
                    </span>
                  )}
                </>
              )}
              {' performed an action'}
            </>
          );
      }
    } catch (error) {
      return `${activity.user?.username || 'Someone'} performed an action`;
    }
  };

  const renderReview = (review: Review) => (
    <ReviewItem key={review.id}>
      <ReviewAlbumCover 
        src={review.album_cover || '/static/music/default-album.svg'} 
        alt={review.album_title}
        onClick={() => review.album_discogs_id ? navigate(`/albums/${review.album_discogs_id}/`) : navigate(`/review/${review.id}/`)}
        title={review.album_discogs_id ? 'View album details' : 'View review'}
        onError={(e) => {
          (e.target as HTMLImageElement).src = '/static/music/default-album.svg';
        }}
      />
      <ReviewContentWrapper>
        <ReviewHeader>
          <div>
            <ReviewAlbumTitle>
              <ReviewTitleLink onClick={() => navigate(`/review/${review.id}/`)}>
                {review.album_title}
                {review.is_pinned && ' 📌'}
              </ReviewTitleLink>
            </ReviewAlbumTitle>
            <ReviewAlbumArtist>
              {review.album_artist}
              {review.album_year && ` • ${review.album_year}`}
            </ReviewAlbumArtist>
          </div>
          <ReviewHeaderRight>
            <ReviewRatingSection>
              <ReviewRating>{review.rating}/10</ReviewRating>
              <ReviewEngagement>
                <span>{review.likes_count} likes</span>
                <span>{review.comments_count} comments</span>
              </ReviewEngagement>
            </ReviewRatingSection>
          </ReviewHeaderRight>
        </ReviewHeader>
        <ReviewContent>
          {renderFormattedText(review.content)}
        </ReviewContent>
        
        {/* Show genres for this review */}
        {review.user_genres && review.user_genres.length > 0 && (
          <div style={{ marginBottom: '8px' }}>
            <GenresList>
              {review.user_genres.map(genre => (
                <GenreTag key={genre.id}>{genre.name}</GenreTag>
              ))}
            </GenresList>
          </div>
        )}
        
        <ReviewBottomActions>
          <ReviewMeta>
            {getTimeAgo(review.created_at)}
          </ReviewMeta>
          <ReviewEngagementActions>
            <EngagementButton 
              $active={review.is_liked_by_user}
              onClick={() => handleLikeReview(review.id, review.is_liked_by_user)}
              disabled={likingReviews.has(review.id)}
              title={review.is_liked_by_user ? 'Unlike' : 'Like'}
            >
              {likingReviews.has(review.id) ? '⏳' : '❤️'}
            </EngagementButton>
            {review.likes_count > 0 && (
              <EngagementButton 
                onClick={() => handleShowLikes(review.id)}
                title="See who liked this"
              >
                {review.likes_count} {review.likes_count === 1 ? 'like' : 'likes'}
              </EngagementButton>
            )}
            <EngagementButton 
              onClick={() => navigate(`/review/${review.id}/`)}
              title="View comments"
            >
              💬 {review.comments_count}
            </EngagementButton>
          </ReviewEngagementActions>
        </ReviewBottomActions>
        
        {/* Show action buttons for own profile */}
        {isOwnProfile && (
          <ReviewActions>
            <ActionButton 
              onClick={() => handleEditReview(review.id)}
              title="Edit Review"
            >
              ✏️
            </ActionButton>
            <ActionButton 
              $pinned={review.is_pinned}
              onClick={() => handlePinReview(review.id, review.is_pinned)}
              title={review.is_pinned ? 'Unpin Review' : 'Pin Review'}
            >
              {review.is_pinned ? '📌' : '📍'}
            </ActionButton>
            <ActionButton 
              onClick={() => handleDeleteReview(review.id)}
              title="Delete Review"
            >
              🗑️
            </ActionButton>
          </ReviewActions>
        )}
      </ReviewContentWrapper>
    </ReviewItem>
  );

  useEffect(() => {
    loadData();
  }, [loadData]);
  
  // Load additional data when switching tabs
  useEffect(() => {
    if (activeTab === 'activity') {
      loadActivities();
    } else if (activeTab === 'lists') {
      loadLists();
    }
  }, [activeTab, loadActivities, loadLists]);

  if (loading) {
    return (
      <Container>
        <LoadingDiv>
          <Spinner />
          <p>Loading profile...</p>
        </LoadingDiv>
      </Container>
    );
  }

  if (error || (!loading && !profileUser)) {
    return (
      <Container>
        <BackLink onClick={() => navigate(-1)}>
          ← Back to Home
        </BackLink>
        <ErrorMessage>
          {error || 'User not found'}
        </ErrorMessage>
      </Container>
    );
  }

  if (!profileUser) {
    return (
      <Container>
        <LoadingDiv>
          <Spinner />
          <p>Loading profile...</p>
        </LoadingDiv>
      </Container>
    );
  }

  return (
    <Container>
      <BackLink onClick={() => navigate(-1)}>
        ← Back to Home
      </BackLink>
      
      {/* Profile Banner */}
      <ProfileBanner 
        $backgroundImage={profileUser.banner}
        onClick={isOwnProfile ? handleEditProfile : undefined}
      >
        {isOwnProfile && (
          <BannerOverlay>
            <BannerEditText>Click to edit banner</BannerEditText>
          </BannerOverlay>
        )}
      </ProfileBanner>
      
      <ProfileHeader>
        <ProfileInfo>
          <ProfileAvatar 
            src={profileUser.avatar || '/static/accounts/default-avatar.svg'} 
            alt={profileUser.username}
            onClick={isOwnProfile ? handleEditProfile : undefined}
            onError={(e) => {
              (e.target as HTMLImageElement).src = '/static/accounts/default-avatar.svg';
            }}
            style={{ cursor: isOwnProfile ? 'pointer' : 'default' }}
          />
          <ProfileDetails>
            <ProfileName>
              {profileUser.display_name}
              {profileUser.is_staff && (
                <span 
                  style={{ 
                    marginLeft: '8px', 
                    fontSize: '24px',
                    color: '#3b82f6',
                    fontWeight: 'bold'
                  }}
                  title="Verified Staff"
                >
                  ✓
                </span>
              )}
            </ProfileName>
            <ProfileBio>@{profileUser.username}</ProfileBio>
            {profileUser.location && <ProfileBio>📍 {profileUser.location}</ProfileBio>}
            {profileUser.bio && <ProfileBio>{profileUser.bio}</ProfileBio>}
            {profileUser.favorite_genres && profileUser.favorite_genres.length > 0 && (
              <GenresList>
                {profileUser.favorite_genres.map(genre => (
                  <GenreTag key={genre.id}>{genre.name}</GenreTag>
                ))}
              </GenresList>
            )}
          </ProfileDetails>
        </ProfileInfo>
        
        <ProfileTopRight>
          <ProfileStats>
            <Stat>
              <StatNumber>{profileUser.review_count}</StatNumber>
              <StatLabel>Reviews</StatLabel>
            </Stat>
            <Stat>
              <StatLink onClick={() => navigate(`/users/${profileUser.username}/followers`)}>
                <StatNumber>{profileUser.follower_count}</StatNumber>
                <StatLabel>Followers</StatLabel>
              </StatLink>
            </Stat>
            <Stat>
              <StatLink onClick={() => navigate(`/users/${profileUser.username}/following`)}>
                <StatNumber>{profileUser.following_count}</StatNumber>
                <StatLabel>Following</StatLabel>
              </StatLink>
            </Stat>
          </ProfileStats>
          {isOwnProfile ? (
            <EditProfileButton onClick={handleEditProfile}>
              Edit Profile
            </EditProfileButton>
          ) : user && (
            <FollowButton 
              $isFollowing={profileUser.is_following}
              onClick={handleFollow}
            >
              {profileUser.is_following ? 'Unfollow' : 'Follow'}
            </FollowButton>
          )}
        </ProfileTopRight>
      </ProfileHeader>

      <TabsContainer>
        <TabsList>
          <Tab 
            $active={activeTab === 'reviews'} 
            onClick={() => setActiveTab('reviews')}
          >
            Reviews ({profileUser.review_count})
          </Tab>
          <Tab 
            $active={activeTab === 'activity'} 
            onClick={() => setActiveTab('activity')}
          >
            Activity
          </Tab>
          <Tab 
            $active={activeTab === 'lists'} 
            onClick={() => setActiveTab('lists')}
          >
            Lists
          </Tab>
        </TabsList>
        
        <TabContent>
          {activeTab === 'reviews' && (
            <>
              {/* Most Reviewed Genres Section */}
              {profileUser.most_reviewed_genres && profileUser.most_reviewed_genres.length > 0 && (
                <GenreSection>
                  <GenreSectionTitle>Most Reviewed Genres</GenreSectionTitle>
                  <GenreStatsGrid>
                    {profileUser.most_reviewed_genres.map(genre => (
                      <GenreStatItem key={genre.name}>
                        <GenreStatName>{genre.name}</GenreStatName>
                        <GenreStatCount>{genre.count}</GenreStatCount>
                      </GenreStatItem>
                    ))}
                  </GenreStatsGrid>
                </GenreSection>
              )}

              {/* Favorite Albums Section */}
              {profileUser.favorite_albums && profileUser.favorite_albums.length > 0 && (
                <FavoriteAlbumsSection>
                  <SectionTitle>Favorite Albums</SectionTitle>
                  <FavoriteAlbumsGrid>
                    {profileUser.favorite_albums.map(album => (
                      <FavoriteAlbumItem key={album.id}>
                        <FavoriteAlbumCover 
                          src={album.cover_url || '/static/music/default-album.svg'} 
                          alt={album.title}
                          onClick={() => {
                            if (album.user_review_id) {
                              navigate(`/review/${album.user_review_id}/`);
                            } else {
                              navigate(`/albums/${album.discogs_id}/`);
                            }
                          }}
                          onError={(e) => {
                            (e.target as HTMLImageElement).src = '/static/music/default-album.svg';
                          }}
                        />
                        <FavoriteAlbumInfo>
                          <FavoriteAlbumTitle>{album.title}</FavoriteAlbumTitle>
                          <FavoriteAlbumArtist>{album.artist}</FavoriteAlbumArtist>
                          {album.user_rating && (
                            <FavoriteAlbumRating>★ {album.user_rating}/10</FavoriteAlbumRating>
                          )}
                        </FavoriteAlbumInfo>
                        {isOwnProfile && (
                          <RemoveFavoriteButton 
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRemoveFavoriteAlbum(album.id);
                            }}
                            title="Remove from favorites"
                          >
                            ×
                          </RemoveFavoriteButton>
                        )}
                      </FavoriteAlbumItem>
                    ))}
                  </FavoriteAlbumsGrid>
                </FavoriteAlbumsSection>
              )}

              {/* Pinned Reviews Section */}
              {pinnedReviews.length > 0 && (
                <ReviewsSection>
                  <SectionTitle>Pinned Reviews</SectionTitle>
                  {pinnedReviews.map(renderReview)}
                </ReviewsSection>
              )}
              
              {/* All Reviews Section */}
              <ReviewsSection>
                <SectionTitle>All Reviews</SectionTitle>
                {reviews.length === 0 ? (
                  <NoReviews>No reviews yet.</NoReviews>
                ) : (
                  reviews.map(renderReview)
                )}
              </ReviewsSection>
            </>
          )}
          
          {activeTab === 'activity' && (
            <ActivityFeed>
              {activitiesLoading ? (
                <LoadingDiv>
                  <Spinner />
                  <p>Loading activities...</p>
                </LoadingDiv>
              ) : activities.length === 0 ? (
                <NoActivity>
                  <h3>No activity yet</h3>
                  <p>
                    {isOwnProfile 
                      ? 'Start reviewing albums to see your activity here!'
                      : `${profileUser.username} hasn't been active yet.`
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
                      <ActivityTime>{formatActivityTime(activity.created_at)}</ActivityTime>
                      
                      {/* Show review content for review activities */}
                      {activity.activity_type === 'review_created' && activity.review_details?.content && (
                        <ActivityReviewContent>
                          "{activity.review_details.content}"
                        </ActivityReviewContent>
                      )}
                      
                      {/* Show comment content for comment activities */}
                      {activity.comment_details && (
                        <ActivityCommentContent>
                          "{activity.comment_details.content}"
                        </ActivityCommentContent>
                      )}
                    </ActivityContent>
                    
                    {/* Show album cover for review-related activities */}
                    {activity.review_details?.album?.cover_url && (
                      <ActivityAlbumCover 
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
          )}
          
          {activeTab === 'lists' && (
            <div>
              {isOwnProfile && (
                <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'flex-end' }}>
                  <button
                    onClick={() => {
                      setShowCreateListModal(true);
                      setProfileError(''); // Clear any errors when opening modal
                      setSuccess(''); // Clear any success messages when opening modal
                    }}
                    style={{
                      background: '#ff6b35',
                      color: 'white',
                      border: 'none',
                      borderRadius: '12px',
                      padding: '12px 24px',
                      fontSize: '16px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#e55a31'}
                    onMouseLeave={(e) => e.currentTarget.style.background = '#ff6b35'}
                  >
                    Create List
                  </button>
                </div>
              )}
              
              {listsLoading ? (
                <LoadingDiv>
                  <Spinner />
                  <p>Loading lists...</p>
                </LoadingDiv>
              ) : lists.length === 0 ? (
                <NoActivity>
                  <h3>No lists yet</h3>
                  <p>
                    {isOwnProfile 
                      ? 'Create your first list to organize your favorite albums!'
                      : `${profileUser.username} hasn't created any lists yet.`
                    }
                  </p>
                </NoActivity>
              ) : (
                <div style={{ display: 'grid', gap: '24px' }}>
                  {lists.map((list) => (
                    <div 
                      key={list.id}
                      style={{
                        background: 'white',
                        borderRadius: '16px',
                        padding: '24px',
                        border: '1px solid #e5e7eb',
                        cursor: 'pointer',
                        transition: 'transform 0.2s ease',
                      }}
                      onClick={() => navigate(`/lists/${list.id}`)}
                      onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                      onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                        <div>
                          <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '8px', color: '#111827' }}>
                            {list.name}
                          </h3>
                          {list.description && (
                            <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '12px' }}>
                              {list.description}
                            </p>
                          )}
                          <div style={{ display: 'flex', gap: '16px', fontSize: '14px', color: '#9ca3af' }}>
                            <span>{list.album_count} {list.album_count === 1 ? 'album' : 'albums'}</span>
                            <span>{list.likes_count} {list.likes_count === 1 ? 'like' : 'likes'}</span>
                          </div>
                        </div>
                        <div style={{ display: 'flex', gap: '8px' }}>
                          {list.first_albums.slice(0, 4).map((album: any, index: number) => (
                            album.cover_url && (
                              <img
                                key={album.id}
                                src={album.cover_url}
                                alt={album.title}
                                style={{
                                  width: '40px',
                                  height: '40px',
                                  borderRadius: '4px',
                                  objectFit: 'cover',
                                  border: '1px solid #e5e7eb'
                                }}
                                onError={(e) => {
                                  (e.target as HTMLImageElement).style.display = 'none';
                                }}
                              />
                            )
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </TabContent>
      </TabsContainer>

      {/* Edit Profile Modal */}
      <EditProfileModal $visible={showEditModal}>
        <ModalContent>
          <ModalHeader>
            <ModalTitle>Edit Profile</ModalTitle>
            <CloseButton onClick={() => setShowEditModal(false)}>×</CloseButton>
          </ModalHeader>
          
          {success && (
            <SuccessMessage>
              {success}
            </SuccessMessage>
          )}
          
          {profileError && (
            <ErrorMessage>
              {profileError}
            </ErrorMessage>
          )}
          
          <FormGroup>
            <Label>Name</Label>
            <Input
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              placeholder="Enter your name"
            />
          </FormGroup>
          
          <FormGroup>
            <Label>Location</Label>
            <Input
              value={editLocation}
              onChange={(e) => setEditLocation(e.target.value)}
              placeholder="Enter your location"
            />
          </FormGroup>
          
          <FormGroup>
            <Label>Bio</Label>
            <Textarea
              value={editBio}
              onChange={(e) => setEditBio(e.target.value)}
              placeholder="Tell us about yourself..."
              maxLength={500}
            />
          </FormGroup>
          
          <FormGroup>
            <Label>Favorite Genres</Label>
            <GenreGrid>
              {availableGenres.map(genre => (
                <GenreOption key={genre.id}>
                  <input
                    type="checkbox"
                    checked={editFavoriteGenres.includes(genre.name)}
                    onChange={() => handleGenreToggle(genre.name)}
                  />
                  {genre.name}
                </GenreOption>
              ))}
            </GenreGrid>
          </FormGroup>
          
          <FileUploadSection>
            <div>
              <FileUploadContainer>
                <FileUploadLabel>Profile Picture</FileUploadLabel>
                <FileUploadHint>Upload a square image (recommended: 400x400px)</FileUploadHint>
                <FileUploadButton type="button" onClick={handleAvatarButtonClick}>
                  📷 Choose Avatar
                </FileUploadButton>
                <HiddenFileInput
                  id="avatar-input"
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarChange}
                />
              </FileUploadContainer>
              
              {avatarPreview && (
                <AvatarPreviewContainer>
                  <AvatarPreviewImage
                    src={avatarPreview}
                    alt="Avatar Preview"
                  />
                  <div>
                    <PreviewLabel>Avatar Preview</PreviewLabel>
                    <RemoveButton onClick={handleRemoveAvatar}>
                      Remove
                    </RemoveButton>
                  </div>
                </AvatarPreviewContainer>
              )}
            </div>

            <div>
              <FileUploadContainer>
                <FileUploadLabel>Banner Image</FileUploadLabel>
                <FileUploadHint>Upload a wide image (recommended: 1200x400px)</FileUploadHint>
                <FileUploadButton type="button" onClick={handleBannerButtonClick}>
                  🖼️ Choose Banner
                </FileUploadButton>
                <HiddenFileInput
                  id="banner-input"
                  type="file"
                  accept="image/*"
                  onChange={handleBannerChange}
                />
              </FileUploadContainer>
              
              {bannerPreview && (
                <BannerPreviewContainer>
                  <PreviewLabel>Banner Preview</PreviewLabel>
                  <BannerPreviewImage
                    src={bannerPreview}
                    alt="Banner Preview"
                  />
                  <RemoveButton onClick={handleRemoveBanner}>
                    Remove
                  </RemoveButton>
                </BannerPreviewContainer>
              )}
            </div>
          </FileUploadSection>
         
          <SaveButton 
            onClick={handleSaveProfile}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </SaveButton>
        </ModalContent>
      </EditProfileModal>

      {/* Create List Modal */}
      <EditProfileModal $visible={showCreateListModal}>
        <ModalContent>
          <ModalHeader>
            <ModalTitle>Create New List</ModalTitle>
            <CloseButton onClick={() => {
              setShowCreateListModal(false);
              setCreateListName('');
              setCreateListDescription('');
              setProfileError(''); // Clear error when closing
              setSuccess(''); // Clear success when closing
            }}>×</CloseButton>
          </ModalHeader>
          
          {success && (
            <SuccessMessage>
              {success}
            </SuccessMessage>
          )}
          
          {profileError && (
            <ErrorMessage>
              {profileError}
            </ErrorMessage>
          )}
          
          <FormGroup>
            <Label>List Name *</Label>
            <Input
              value={createListName}
              onChange={(e) => setCreateListName(e.target.value)}
              placeholder="Enter list name"
              maxLength={100}
            />
          </FormGroup>
          
          <FormGroup>
            <Label>Description</Label>
            <Textarea
              value={createListDescription}
              onChange={(e) => setCreateListDescription(e.target.value)}
              placeholder="Describe your list (optional)"
              maxLength={500}
            />
          </FormGroup>
          
          <SaveButton 
            onClick={handleCreateList}
            disabled={creatingList || !createListName.trim()}
            style={{
              opacity: creatingList || !createListName.trim() ? 0.6 : 1,
            }}
          >
            {creatingList ? 'Creating...' : 'Create List'}
          </SaveButton>
        </ModalContent>
      </EditProfileModal>

      {/* Likes Modal */}
      <LikesModal $visible={showLikesModal} onClick={() => setShowLikesModal(false)}>
        <LikesModalContent onClick={(e) => e.stopPropagation()}>
          <LikesModalHeader>
            <LikesModalTitle>Likes</LikesModalTitle>
            <CloseButton onClick={() => setShowLikesModal(false)}>×</CloseButton>
          </LikesModalHeader>
          
          {loadingLikes ? (
            <div>Loading...</div>
          ) : likesData && likesData.users.length > 0 ? (
            likesData.users.map(user => (
              <LikeUserItem key={user.id}>
                <LikeUserAvatar 
                  src={user.avatar || '/static/accounts/default-avatar.svg'}
                  alt={user.username}
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/static/accounts/default-avatar.svg';
                  }}
                />
                <LikeUserName>
                  {user.username}
                </LikeUserName>
              </LikeUserItem>
            ))
          ) : (
            <div>No likes yet.</div>
          )}
        </LikesModalContent>
      </LikesModal>

      {/* Edit Review Modal */}
      <EditReviewModal
        isVisible={showEditReviewModal}
        reviewId={editingReviewId}
        onClose={handleCloseEditReviewModal}
        onSave={handleSaveEditReview}
      />
    </Container>
  );
};

export default ProfilePage; 
import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';

const NavbarContainer = styled.nav`
  background: white;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
`;

const Logo = styled.a`
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  text-decoration: none;
  cursor: pointer;
`;

const NavButtons = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
`;

const NavBtn = styled(Link)<{ $active?: boolean }>`
  padding: 8px 20px;
  border: 1px solid #e5e7eb;
  background: ${props => props.$active ? '#111827' : 'white'};
  color: ${props => props.$active ? 'white' : '#374151'};
  border-color: ${props => props.$active ? '#111827' : '#e5e7eb'};
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  text-decoration: none;

  &:hover {
    background: ${props => props.$active ? '#374151' : '#f9fafb'};
  }
`;

const NavLinks = styled.div<{ $loggedIn: boolean }>`
  display: ${props => props.$loggedIn ? 'flex' : 'none'};
  gap: 12px;
`;

const LogoutBtn = styled.button`
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  font-size: 14px;

  &:hover {
    background: #f9fafb;
  }
`;

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleLogoClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (user) {
      navigate('/');
    } else {
      navigate('/login');
    }
  };

  return (
    <NavbarContainer>
      <Logo href="/" onClick={handleLogoClick}>halfnote API Testing Interface</Logo>
      
      <NavButtons>
        <NavLinks $loggedIn={!!user}>
          <NavBtn to="/" $active={location.pathname === '/'}>
            Home
          </NavBtn>
          <NavBtn to="/activity" $active={location.pathname === '/activity'}>
            Activity
          </NavBtn>
          {user && (
            <NavBtn to={`/users/${user.username}`} $active={location.pathname.includes('/users/')}>
              Profile
            </NavBtn>
          )}
          <LogoutBtn onClick={handleLogout}>
            Logout
          </LogoutBtn>
        </NavLinks>
      </NavButtons>
    </NavbarContainer>
  );
};

export default Navbar; 
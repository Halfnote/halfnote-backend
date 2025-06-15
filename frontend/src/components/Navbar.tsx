import React, { useState } from 'react';
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

  @media (max-width: 768px) {
    flex-wrap: wrap;
    padding: 12px 16px;
  }
`;

const Logo = styled.a`
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  text-decoration: none;
  cursor: pointer;
`;

const MenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;

  @media (max-width: 768px) {
    display: block;
  }
`;

const NavButtons = styled.div<{ $menuOpen: boolean }>`
  display: flex;
  gap: 12px;
  align-items: center;

  @media (max-width: 768px) {
    flex-basis: 100%;
    flex-direction: column;
    align-items: stretch;
    display: ${props => (props.$menuOpen ? 'flex' : 'none')};
    gap: 8px;
  }
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

  @media (max-width: 768px) {
    width: 100%;
    text-align: center;
  }

  &:hover {
    background: ${props => props.$active ? '#374151' : '#f9fafb'};
  }
`;

const SearchNav = styled.div<{ $disabled?: boolean }>`
  position: relative;
  background: #f3f4f6;
  border-radius: 25px;
  display: flex;
  align-items: center;
  padding: 8px 16px;
  min-width: 200px;

  @media (max-width: 768px) {
    width: 100%;
  }
  
  &::before {
    content: "🔍";
    margin-right: 8px;
  }
`;

const SearchInput = styled.input<{ $disabled?: boolean }>`
  border: none;
  background: none;
  outline: none;
  flex: 1;
  padding: 4px 8px;
  font-size: 14px;
  color: ${props => props.$disabled ? '#9ca3af' : 'inherit'};
  cursor: ${props => props.$disabled ? 'not-allowed' : 'text'};

  &::placeholder {
    color: #9ca3af;
  }
`;

const NavLinks = styled.div<{ $loggedIn: boolean }>`
  display: ${props => props.$loggedIn ? 'flex' : 'none'};
  gap: 12px;

  @media (max-width: 768px) {
    flex-direction: column;
    width: 100%;
  }
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

  @media (max-width: 768px) {
    width: 100%;
  }

  &:hover {
    background: #f9fafb;
  }
`;

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim() && user) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleMenu = () => {
    setMenuOpen(prev => !prev);
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
      <MenuButton onClick={toggleMenu} aria-label="Toggle menu">☰</MenuButton>

      <NavButtons $menuOpen={menuOpen}>
        <form onSubmit={handleSearch}>
          <SearchNav $disabled={!user}>
            <SearchInput
              type="text"
              placeholder="Search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              disabled={!user}
              $disabled={!user}
            />
          </SearchNav>
        </form>

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
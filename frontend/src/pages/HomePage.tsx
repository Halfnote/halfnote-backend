import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';

const Container = styled.div`
  max-width: 600px;
  margin: 60px auto;
  padding: 0 20px;
`;

const MainCard = styled.div`
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  text-align: center;
  margin-bottom: 32px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 16px;
`;

const Subtitle = styled.p`
  color: #6b7280;
  margin-bottom: 32px;
`;

const Links = styled.div`
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
`;

const Btn = styled.button`
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
  display: inline-block;
`;

const BtnPrimary = styled(Btn)`
  background: #111827;
  color: white;

  &:hover {
    background: #374151;
  }
`;

const BtnSecondary = styled(Btn)`
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;

  &:hover {
    background: #f9fafb;
  }
`;

const AuthSection = styled.div`
  max-width: 400px;
  margin: 0 auto;
`;

const AuthCard = styled.div`
  background: white;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #e5e7eb;
`;

const AuthTabs = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
`;

const TabBtn = styled.button<{ $active: boolean }>`
  padding: 8px 20px;
  border: 1px solid #e5e7eb;
  background: ${props => props.$active ? '#111827' : 'white'};
  color: ${props => props.$active ? 'white' : '#374151'};
  border-color: ${props => props.$active ? '#111827' : '#e5e7eb'};
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  flex: 1;
  text-align: center;

  &:hover {
    background: ${props => props.$active ? '#374151' : '#f9fafb'};
  }
`;

const FormGroup = styled.div`
  margin: 16px 0;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  font-size: 14px;
  color: #374151;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const ErrorMessage = styled.div`
  color: #dc2626;
  font-size: 14px;
  margin-top: 8px;
  padding: 8px 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
`;

const SuccessMessage = styled.div`
  color: #059669;
  font-size: 14px;
  margin-top: 8px;
  padding: 8px 12px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
`;

const FormButton = styled.button`
  width: 100%;
  padding: 12px 24px;
  background: #111827;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #374151;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const WelcomeSection = styled.div`
  text-align: center;
`;

const WelcomeTitle = styled.h2`
  font-size: 24px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 16px;
`;

const UserInfo = styled.p`
  color: #6b7280;
  margin-bottom: 24px;
`;



const SearchBox = styled.div`
  margin-bottom: 32px;
  display: flex;
  justify-content: center;
  
  form {
    display: flex;
    gap: 12px;
    align-items: center;
    width: 100%;
    max-width: 700px;
  }
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 16px 20px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-size: 18px;
  min-height: 56px;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  &::placeholder {
    color: #9ca3af;
  }
`;

const SearchButton = styled(BtnPrimary)`
  padding: 16px 24px;
  border-radius: 12px;
  font-size: 16px;
  min-height: 56px;
  white-space: nowrap;
`;

const HomePage: React.FC = () => {
  const { user, login, register, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    bio: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      if (activeTab === 'login') {
        if (!formData.username || !formData.password) {
          throw new Error('Username and password are required');
        }
        await login(formData.username, formData.password);
        setSuccess('Login successful!');
        // Clear form
        setFormData({ username: '', email: '', password: '', bio: '' });
      } else {
        if (!formData.username || !formData.email || !formData.password) {
          throw new Error('Username, email, and password are required');
        }
        await register(formData.username, formData.email, formData.password);
        setSuccess('Registration successful!');
        // Clear form
        setFormData({ username: '', email: '', password: '', bio: '' });
      }
    } catch (err: any) {
      console.error('Auth error:', err);
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleLogout = () => {
    logout();
    setSuccess('Logged out successfully');
  };

  if (user) {
    return (
      <Container>
        <MainCard>
          <WelcomeSection>
            <WelcomeTitle>Welcome back, {user.name || user.username}!</WelcomeTitle>
            <UserInfo>
              Ready to discover and review some music?
            </UserInfo>
            
            <SearchBox>
              <form onSubmit={handleSearch}>
                <SearchInput
                  type="text"
                  placeholder="Search for albums, artists, or users..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <SearchButton type="submit">Search</SearchButton>
              </form>
            </SearchBox>

            {success && <SuccessMessage>{success}</SuccessMessage>}
          </WelcomeSection>
        </MainCard>
      </Container>
    );
  }

  return (
    <Container>
      <MainCard>
        <Title>BoomBoxd</Title>
        <Subtitle>Discover, rate, and review music with fellow enthusiasts</Subtitle>
        <Links>
          <BtnPrimary onClick={() => navigate('/search?q=')}>
            Explore Music
          </BtnPrimary>
          <BtnSecondary onClick={() => document.getElementById('auth-section')?.scrollIntoView()}>
            Join Now
          </BtnSecondary>
        </Links>
      </MainCard>

      <AuthSection id="auth-section">
        <AuthCard>
          <AuthTabs>
            <TabBtn 
              $active={activeTab === 'login'} 
              onClick={() => {
                setActiveTab('login');
                setError('');
                setSuccess('');
              }}
            >
              Login
            </TabBtn>
            <TabBtn 
              $active={activeTab === 'register'} 
              onClick={() => {
                setActiveTab('register');
                setError('');
                setSuccess('');
              }}
            >
              Register
            </TabBtn>
          </AuthTabs>

          <form onSubmit={handleSubmit}>
            <FormGroup>
              <Label htmlFor="username">Username</Label>
              <Input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
                autoComplete="username"
              />
            </FormGroup>

            {activeTab === 'register' && (
              <FormGroup>
                <Label htmlFor="email">Email</Label>
                <Input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  autoComplete="email"
                />
              </FormGroup>
            )}

            <FormGroup>
              <Label htmlFor="password">Password</Label>
              <Input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                autoComplete={activeTab === 'login' ? 'current-password' : 'new-password'}
              />
            </FormGroup>

            {error && <ErrorMessage>{error}</ErrorMessage>}
            {success && <SuccessMessage>{success}</SuccessMessage>}

            <FormButton type="submit" disabled={loading}>
              {loading ? 'Please wait...' : activeTab === 'login' ? 'Login' : 'Register'}
            </FormButton>
          </form>
        </AuthCard>
      </AuthSection>
    </Container>
  );
};

export default HomePage; 
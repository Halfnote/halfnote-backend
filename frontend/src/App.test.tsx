import React from 'react';
import { render, screen } from '@testing-library/react';
// Mock dependencies used within the App component to avoid loading their real
// implementations during this simple rendering test.
jest.mock('./components/Navbar', () => () => <div>Navbar</div>, { virtual: true });
jest.mock('./components/ProtectedRoute', () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => <div>{children}</div>
}), { virtual: true });
jest.mock('./pages/HomePage', () => () => <div>HomePage</div>, { virtual: true });
jest.mock('./pages/LoginPage', () => () => <div>LoginPage</div>, { virtual: true });
jest.mock('./pages/RegisterPage', () => () => <div>RegisterPage</div>, { virtual: true });
jest.mock('./pages/ProfilePage', () => () => <div>ProfilePage</div>, { virtual: true });
jest.mock('./pages/ReviewDetailPage', () => () => <div>ReviewDetailPage</div>, { virtual: true });
jest.mock('./pages/SearchResultsPage', () => () => <div>SearchResultsPage</div>, { virtual: true });
jest.mock('./pages/ActivityPage', () => () => <div>ActivityPage</div>, { virtual: true });
jest.mock('./pages/FollowersPage', () => () => <div>FollowersPage</div>, { virtual: true });
jest.mock('./pages/FollowingPage', () => () => <div>FollowingPage</div>, { virtual: true });

import App from './App';

// Mock react-router-dom to avoid ESM resolution issues during tests
jest.mock(
  'react-router-dom',
  () => ({
    BrowserRouter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    Routes: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    Route: () => null,
    Navigate: () => null,
    Link: ({ children }: { children: React.ReactNode }) => <a>{children}</a>,
    useLocation: () => ({ pathname: '/' }),
    useNavigate: () => jest.fn()
  }),
  { virtual: true }
);

// Mock AuthContext to keep the application in a loading state
jest.mock('./contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useAuth: () => ({ user: null, isLoading: true })
}));

test('shows loading message on initial render', () => {
  render(<App />);
  expect(screen.getByText('Loading...')).toBeInTheDocument();
});

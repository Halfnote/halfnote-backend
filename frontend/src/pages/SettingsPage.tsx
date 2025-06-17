import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
`;

const Title = styled.h1`
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: 600;
  color: #111827;
`;

const SettingsPage: React.FC = () => {
  return (
    <Container>
      <Title>Settings</Title>
      <p>Settings page coming soon...</p>
    </Container>
  );
};

export default SettingsPage; 
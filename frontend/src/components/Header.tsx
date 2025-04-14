import React from 'react';
import { AppBar, Toolbar, Typography, Box, Container } from '@mui/material';
import { Link } from 'react-router-dom';

interface HeaderProps {
  title?: string;
}

const Header: React.FC<HeaderProps> = ({ title = 'CI/CD Dashboard' }) => {
  return (
    <AppBar position="static" color="primary" sx={{ mb: 4 }}>
      <Container>
        <Toolbar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography 
              variant="h5" 
              component={Link} 
              to="/" 
              sx={{ 
                textDecoration: 'none', 
                color: 'white',
                fontWeight: 'bold'
              }}
            >
              {title}
            </Typography>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header; 
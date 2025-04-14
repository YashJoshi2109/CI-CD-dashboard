import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Box, Button } from '@mui/material';
import Dashboard from './pages/Dashboard';
import BuildLogsPage from './pages/BuildLogsPage';

const App: React.FC = () => {
    return (
        <Router>
            <Box sx={{ flexGrow: 1 }}>
                <AppBar position="static">
                    <Toolbar>
                        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                            CI/CD Dashboard
                        </Typography>
                        <Button color="inherit" component={Link} to="/">
                            Dashboard
                        </Button>
                    </Toolbar>
                </AppBar>
                <Container>
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/logs/:pipelineId" element={<BuildLogsPage />} />
                    </Routes>
                </Container>
            </Box>
        </Router>
    );
};

export default App;

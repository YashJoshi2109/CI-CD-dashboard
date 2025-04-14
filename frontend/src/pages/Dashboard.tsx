import React, { useEffect, useState } from 'react';
import { Container, Typography, Button, Box, CircularProgress, Alert } from '@mui/material';
import PipelineCard from '../components/PipelineCard';
import { PipelineStatus } from '../types';
import { getPipelineStatus, triggerBuild, triggerRollback } from '../services/api';
import RefreshIcon from '@mui/icons-material/Refresh';

const Dashboard: React.FC = () => {
    const [pipelines, setPipelines] = useState<PipelineStatus[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [refreshing, setRefreshing] = useState(false);

    const fetchPipelines = async () => {
        try {
            setRefreshing(true);
            const response = await getPipelineStatus();
            
            if (response && response.data) {
                setPipelines(response.data || []);
                setError(null); // Clear any previous errors if the request was successful
            } else {
                setPipelines([]);
                console.error('Invalid response format:', response);
                setError('Invalid response from server. Please check backend logs.');
            }
            
        } catch (err) {
            console.error(err);
            setPipelines([]); // Ensure pipelines is always an array
            setError('Failed to fetch pipeline status. Please try again later.');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const handleRollback = async (pipelineId: string) => {
        try {
            await triggerRollback(pipelineId);
            // Show success message
            setError('Rollback triggered successfully');
            // Refresh pipeline status after rollback
            setTimeout(() => fetchPipelines(), 1000);
        } catch (err) {
            console.error('Failed to trigger rollback:', err);
            setError('Failed to trigger rollback. Please try again later.');
        }
    };

    const handleTriggerBuild = async (pipelineId: string) => {
        try {
            await triggerBuild(pipelineId); 
            // Show success message
            setError('Build triggered successfully');
            // Refresh pipeline status after build
            setTimeout(() => fetchPipelines(), 1000);
        } catch (err) {
            console.error('Failed to trigger build:', err);
            setError('Failed to trigger build. Please try again later.');
        }
    };

    const handleTriggerRollback = async (pipelineId: string) => {
        // ... existing code ...
    };

    useEffect(() => {
        fetchPipelines();
        // Set up polling every 30 seconds
        const interval = setInterval(fetchPipelines, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
                <Typography variant="h4" component="h1">
                    CI/CD Dashboard
                </Typography>
                <Button 
                    variant="contained" 
                    onClick={fetchPipelines} 
                    disabled={refreshing}
                    startIcon={<RefreshIcon />}
                >
                    {refreshing ? 'Refreshing...' : 'Refresh'}
                </Button>
            </Box>

            {!loading && error && (
                <Alert 
                    severity={error.includes('success') ? 'success' : 'error'} 
                    sx={{ mb: 2 }}
                    onClose={() => setError(null)}
                >
                    {error}
                </Alert>
            )}

            {!loading && !error && !pipelines.length && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                    <Typography variant="body1" gutterBottom>
                        No pipelines found. This could be due to:
                    </Typography>
                    <ul>
                        <li>Jenkins server is not running or not accessible</li>
                        <li>Incorrect Jenkins credentials in the backend .env file</li>
                        <li>No jobs/pipelines configured in Jenkins</li>
                    </ul>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                        Please check your Jenkins configuration at http://localhost:8080
                    </Typography>
                </Alert>
            )}

            {loading && !refreshing ? (
                <Box display="flex" justifyContent="center" my={4}>
                    <CircularProgress />
                </Box>
            ) : (
                !pipelines || pipelines.length === 0 ? (
                    <Alert severity="info">
                        No pipelines found. Please check your Jenkins configuration.
                    </Alert>
                ) : (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', margin: -1 }}>
                        {pipelines.map((pipeline) => (
                            <Box sx={{ width: { xs: '100%', sm: '50%', md: '33.33%' }, padding: 1 }} key={pipeline.id}>
                                <PipelineCard
                                    pipeline={pipeline}
                                    onRollback={handleRollback}
                                    onTriggerBuild={handleTriggerBuild}
                                />
                            </Box>
                        ))}
                    </Box>
                )
            )}
        </Container>
    );
};

export default Dashboard; 
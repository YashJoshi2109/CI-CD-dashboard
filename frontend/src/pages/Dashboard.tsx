import React, { useEffect, useState } from 'react';
import { Container, Typography, Button, Box, CircularProgress, Alert, AlertTitle } from '@mui/material';
import PipelineCard from '../components/PipelineCard';
import { PipelineStatus } from '../types';
import { getPipelineStatuses, triggerBuild, triggerRollback } from '../services/api';
import RefreshIcon from '@mui/icons-material/Refresh';

const Dashboard: React.FC = () => {
    const [pipelines, setPipelines] = useState<PipelineStatus[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [refreshing, setRefreshing] = useState(false);

    const fetchPipelines = async () => {
        try {
            setError(null);
            const response = await getPipelineStatuses();
            if (response.error) {
                setError(response.error);
                setPipelines([]);
            } else {
                setPipelines(response.data);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch pipelines');
            setPipelines([]);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const handleRollback = async (pipelineId: string) => {
        try {
            const response = await triggerRollback(pipelineId);
            // Show success message
            setError(response.message || 'Rollback triggered successfully');
            // Refresh pipeline status after rollback
            setTimeout(() => fetchPipelines(), 1000);
        } catch (err) {
            console.error('Failed to trigger rollback:', err);
            setError('Failed to trigger rollback. Please try again later.');
        }
    };

    const handleTriggerBuild = async (pipelineId: string) => {
        try {
            const response = await triggerBuild(pipelineId);
            // Show success message
            setError(response.message || 'Build triggered successfully');
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

    const handleRefresh = () => {
        setRefreshing(true);
        fetchPipelines();
    };

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
                <Typography variant="h4" component="h1">
                    CI/CD Dashboard
                </Typography>
                <Button 
                    variant="contained" 
                    onClick={handleRefresh} 
                    disabled={refreshing}
                    startIcon={<RefreshIcon />}
                >
                    {refreshing ? 'Refreshing...' : 'REFRESH'}
                </Button>
            </Box>

            {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                    <CircularProgress />
                </Box>
            )}

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    <AlertTitle>Error</AlertTitle>
                    {error}
                </Alert>
            )}

            {!loading && !error && pipelines.length === 0 && (
                <Box>
                    <Alert severity="warning" sx={{ mb: 2 }}>
                        <AlertTitle>No pipelines found. This could be due to:</AlertTitle>
                        <ul>
                            <li>Jenkins server is not running or not accessible</li>
                            <li>Incorrect Jenkins credentials in the backend .env file</li>
                            <li>No jobs/pipelines configured in Jenkins</li>
                        </ul>
                        Please check your Jenkins configuration at http://localhost:8081
                    </Alert>
                    <Alert severity="info">
                        No pipelines found. Please check your Jenkins configuration.
                    </Alert>
                </Box>
            )}

            {!loading && !error && pipelines.length > 0 && (
                <Box sx={{ display: 'grid', gap: 2 }}>
                    {pipelines.map((pipeline) => (
                        <PipelineCard
                            key={pipeline.id}
                            pipeline={pipeline}
                            onRollback={handleRollback}
                            onTriggerBuild={handleTriggerBuild}
                        />
                    ))}
                </Box>
            )}
        </Container>
    );
};

export default Dashboard; 
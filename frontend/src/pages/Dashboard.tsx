import React, { useEffect, useState } from 'react';
import { Container, Grid, Typography, Button, Box } from '@mui/material';
import PipelineCard from '../components/PipelineCard';
import { PipelineStatus } from '../types';
import { getPipelineStatus, triggerRollback } from '../services/api';

const Dashboard: React.FC = () => {
    const [pipelines, setPipelines] = useState<PipelineStatus[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchPipelines = async () => {
        try {
            setLoading(true);
            const response = await getPipelineStatus();
            setPipelines(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to fetch pipeline status');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleRollback = async (pipelineId: string) => {
        try {
            await triggerRollback(pipelineId);
            // Refresh pipeline status after rollback
            fetchPipelines();
        } catch (err) {
            console.error('Failed to trigger rollback:', err);
        }
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
                <Button variant="contained" onClick={fetchPipelines} disabled={loading}>
                    Refresh
                </Button>
            </Box>

            {error && (
                <Typography color="error" gutterBottom>
                    {error}
                </Typography>
            )}

            <Grid container spacing={3}>
                {pipelines.map((pipeline) => (
                    <Grid item xs={12} sm={6} md={4} key={pipeline.id}>
                        <PipelineCard
                            pipeline={pipeline}
                            onRollback={handleRollback}
                        />
                    </Grid>
                ))}
            </Grid>
        </Container>
    );
};

export default Dashboard; 
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Typography, Box, Button } from '@mui/material';
import BuildLogs from '../components/BuildLogs';
import { BuildLog } from '../types';
import { getBuildLogs } from '../services/api';

const BuildLogsPage: React.FC = () => {
    const { pipelineId } = useParams<{ pipelineId: string }>();
    const [logs, setLogs] = useState<BuildLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchLogs = async () => {
        if (!pipelineId) return;

        try {
            setLoading(true);
            const response = await getBuildLogs(pipelineId);
            setLogs(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to fetch build logs');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
        // Set up polling every 30 seconds
        const interval = setInterval(fetchLogs, 30000);
        return () => clearInterval(interval);
    }, [pipelineId]);

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
                <Typography variant="h4" component="h1">
                    Build Logs
                </Typography>
                <Button variant="contained" onClick={fetchLogs} disabled={loading}>
                    Refresh
                </Button>
            </Box>

            {error && (
                <Typography color="error" gutterBottom>
                    {error}
                </Typography>
            )}

            <BuildLogs logs={logs} />
        </Container>
    );
};

export default BuildLogsPage; 
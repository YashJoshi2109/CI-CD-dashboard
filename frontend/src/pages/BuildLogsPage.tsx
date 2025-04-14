import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
    Container, Typography, Box, Button, CircularProgress, 
    Paper, Divider, Alert, Chip, IconButton, Card, CardContent, 
    Stack
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import RefreshIcon from '@mui/icons-material/Refresh';
import DownloadIcon from '@mui/icons-material/Download';
import BuildLogs from '../components/BuildLogs';
import { BuildLog } from '../types';
import { getBuildLogs } from '../services/api';

const BuildLogsPage: React.FC = () => {
    const { pipelineId } = useParams<{ pipelineId: string }>();
    const navigate = useNavigate();
    const [logs, setLogs] = useState<BuildLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [pipelineName, setPipelineName] = useState<string | null>(null);

    const fetchLogs = useCallback(async () => {
        if (!pipelineId) return;

        try {
            setLoading(true);
            const response = await getBuildLogs(pipelineId);
            setLogs(response.data || []);
            
            // Remove setting pipeline name from logs
            // if (response.data && response.data.length > 0) {
            //     setPipelineName(response.data[0].pipeline_name); 
            // }
            
            setError(null);
        } catch (err) {
            console.error(err);
            setError('Failed to fetch build logs. Please try again later.');
        } finally {
            setLoading(false);
        }
    }, [pipelineId]);

    useEffect(() => {
        fetchLogs();
        // Set up polling every 30 seconds
        const interval = setInterval(fetchLogs, 30000);
        return () => clearInterval(interval);
    }, [pipelineId, fetchLogs]);

    const downloadLogs = (log: BuildLog) => {
        const element = document.createElement('a');
        const file = new Blob([log.log_content], { type: 'text/plain' });
        element.href = URL.createObjectURL(file);
        element.download = `build-log-${pipelineId}-${new Date(log.timestamp).toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };

    const handleBack = () => {
        navigate(-1);
    };

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
                <Stack direction="row" spacing={2} alignItems="center">
                    <IconButton onClick={handleBack} size="small" color="primary">
                        <ArrowBackIcon />
                    </IconButton>
                    <Typography variant="h4" component="h1">
                        {pipelineName ? `${pipelineName} Logs` : 'Build Logs'}
                    </Typography>
                </Stack>
                <Button 
                    variant="contained" 
                    onClick={fetchLogs} 
                    disabled={loading}
                    startIcon={<RefreshIcon />}
                >
                    {loading ? 'Loading...' : 'Refresh'}
                </Button>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {loading && logs.length === 0 ? (
                <Box display="flex" justifyContent="center" my={4}>
                    <CircularProgress />
                </Box>
            ) : logs.length === 0 ? (
                <Alert severity="info">
                    No build logs found for this pipeline.
                </Alert>
            ) : (
                <Box>
                    <Typography variant="h6" component="h2" gutterBottom>
                        Logs for Pipeline: {pipelineId}
                    </Typography>
                    {logs.map((log) => (
                        <Card key={log.id} sx={{ mb: 3, borderRadius: 2, overflow: 'hidden' }}>
                            <Box 
                                display="flex" 
                                justifyContent="space-between" 
                                alignItems="center" 
                                sx={{ 
                                    backgroundColor: log.status.toLowerCase() === 'success' ? '#e8f5e9' : 
                                                   log.status.toLowerCase() === 'failed' ? '#ffebee' : '#f5f5f5',
                                    p: 2
                                }}
                            >
                                <Box>
                                    <Typography variant="body2" color="text.secondary">
                                        {new Date(log.timestamp).toLocaleString()}
                                    </Typography>
                                </Box>
                                <Box display="flex" alignItems="center" gap={2}>
                                    <Chip 
                                        label={log.status} 
                                        color={
                                            log.status.toLowerCase() === 'success' ? 'success' : 
                                            log.status.toLowerCase() === 'failed' ? 'error' : 'default'
                                        }
                                        size="small"
                                    />
                                    <IconButton 
                                        size="small" 
                                        onClick={() => downloadLogs(log)}
                                        title="Download log"
                                    >
                                        <DownloadIcon fontSize="small" />
                                    </IconButton>
                                </Box>
                            </Box>
                            <Divider />
                            <CardContent>
                                <Box>
                                    <Typography variant="subtitle1" fontWeight="bold">
                                        Build from {new Date(log.timestamp).toLocaleDateString()}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {new Date(log.timestamp).toLocaleString()}
                                    </Typography>
                                </Box>
                                <Typography
                                    variant="body2"
                                    component="pre"
                                    sx={{
                                        whiteSpace: 'pre-wrap',
                                        wordBreak: 'break-word',
                                        fontFamily: 'monospace',
                                        fontSize: '0.875rem',
                                        p: 2,
                                        backgroundColor: '#f5f5f5',
                                        borderRadius: 1,
                                        maxHeight: '400px',
                                        overflow: 'auto'
                                    }}
                                >
                                    {log.log_content}
                                </Typography>
                            </CardContent>
                        </Card>
                    ))}
                </Box>
            )}
        </Container>
    );
};

export default BuildLogsPage; 
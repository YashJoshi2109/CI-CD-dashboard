import React from 'react';
import { Card, CardContent, Typography, Button, Chip, Box, Stack } from '@mui/material';
import { PlayArrow, Refresh, History } from '@mui/icons-material';
import { PipelineStatus } from '../types';
import { useNavigate } from 'react-router-dom';

interface PipelineCardProps {
    pipeline: PipelineStatus;
    onRollback: (pipelineId: string) => void;
    onTriggerBuild: (pipelineId: string) => void;
}

const PipelineCard: React.FC<PipelineCardProps> = ({ pipeline, onRollback, onTriggerBuild }) => {
    const navigate = useNavigate();

    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'success':
                return 'success';
            case 'failed':
                return 'error';
            case 'running':
            case 'building':
                return 'warning';
            default:
                return 'default';
        }
    };

    const goToLogs = () => {
        navigate(`/logs/${pipeline.id}`);
    };

    const goToHistory = () => {
        navigate(`/history/${pipeline.id}`);
    };

    return (
        <Card sx={{ 
            minWidth: 275, 
            marginBottom: 2,
            boxShadow: 3,
            borderLeft: `5px solid ${
                getStatusColor(pipeline.status) === 'success' ? '#4caf50' :
                getStatusColor(pipeline.status) === 'error' ? '#f44336' :
                getStatusColor(pipeline.status) === 'warning' ? '#ff9800' : '#9e9e9e'
            }`
        }}>
            <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h5" component="div">
                        {pipeline.name}
                    </Typography>
                    <Chip
                        label={pipeline.status}
                        color={getStatusColor(pipeline.status)}
                        size="small"
                    />
                </Box>
                <Typography color="text.secondary" gutterBottom>
                    Last Build: {new Date(pipeline.last_build_time).toLocaleString()}
                </Typography>
                {pipeline.duration && (
                    <Typography color="text.secondary" gutterBottom>
                        Duration: {pipeline.duration}
                    </Typography>
                )}
                {pipeline.commit_hash && (
                    <Typography color="text.secondary" gutterBottom>
                        Commit: {pipeline.commit_hash.substring(0, 7)}
                    </Typography>
                )}
                
                <Box mt={2}>
                    <Stack direction="row" spacing={1} mb={1}>
                        <Button
                            variant="contained"
                            color="primary"
                            size="small"
                            startIcon={<PlayArrow />}
                            onClick={() => onTriggerBuild(pipeline.id)}
                            disabled={pipeline.status.toLowerCase() === 'running' || pipeline.status.toLowerCase() === 'building'}
                        >
                            Build
                        </Button>
                        
                        <Button
                            variant="outlined"
                            color="error"
                            size="small"
                            onClick={() => onRollback(pipeline.id)}
                            disabled={pipeline.status.toLowerCase() !== 'failed'}
                        >
                            Rollback
                        </Button>
                    </Stack>
                    
                    <Stack direction="row" spacing={1}>
                        <Button
                            variant="outlined"
                            color="info"
                            size="small"
                            onClick={goToLogs}
                        >
                            View Logs
                        </Button>
                        
                        <Button
                            variant="outlined"
                            color="secondary"
                            size="small"
                            startIcon={<History />}
                            onClick={goToHistory}
                        >
                            History
                        </Button>
                    </Stack>
                </Box>
            </CardContent>
        </Card>
    );
};

export default PipelineCard; 
import React from 'react';
import { Card, CardContent, Typography, Button, Chip, Box } from '@mui/material';
import { PipelineStatus } from '../types';
import { triggerRollback } from '../services/api';

interface PipelineCardProps {
    pipeline: PipelineStatus;
    onRollback: (pipelineId: string) => void;
}

const PipelineCard: React.FC<PipelineCardProps> = ({ pipeline, onRollback }) => {
    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'success':
                return 'success';
            case 'failed':
                return 'error';
            case 'running':
                return 'warning';
            default:
                return 'default';
        }
    };

    return (
        <Card sx={{ minWidth: 275, marginBottom: 2 }}>
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
                    <Button
                        variant="contained"
                        color="error"
                        onClick={() => onRollback(pipeline.id)}
                        disabled={pipeline.status.toLowerCase() !== 'failed'}
                    >
                        Rollback
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
};

export default PipelineCard; 
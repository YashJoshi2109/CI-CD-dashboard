import React from 'react';
import { Box, Typography, Paper, Divider } from '@mui/material';
import { BuildLog } from '../types';

interface BuildLogsProps {
    logs: BuildLog[];
}

const BuildLogs: React.FC<BuildLogsProps> = ({ logs }) => {
    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                Build Logs
            </Typography>
            {logs.map((log, index) => (
                <Paper key={log.id} sx={{ p: 2, mb: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="subtitle2">
                            {new Date(log.timestamp).toLocaleString()}
                        </Typography>
                        <Typography
                            variant="caption"
                            color={log.status.toLowerCase() === 'success' ? 'success.main' : 'error.main'}
                        >
                            {log.status}
                        </Typography>
                    </Box>
                    <Divider sx={{ my: 1 }} />
                    <Typography
                        variant="body2"
                        component="pre"
                        sx={{
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                            fontFamily: 'monospace',
                            fontSize: '0.875rem',
                        }}
                    >
                        {log.log_content}
                    </Typography>
                </Paper>
            ))}
        </Box>
    );
};

export default BuildLogs; 
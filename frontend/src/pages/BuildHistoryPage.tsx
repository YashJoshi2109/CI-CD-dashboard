import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getBuildHistory } from '../services/api';
import { BuildHistoryItem, BuildHistoryResponse } from '../types';
import { format } from 'date-fns';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip, CircularProgress } from '@mui/material';
import { CheckCircle, Cancel, HourglassEmpty } from '@mui/icons-material';
import Header from '../components/Header';

const BuildHistoryPage: React.FC = () => {
  const { pipelineId } = useParams<{ pipelineId: string }>();
  const [buildHistory, setBuildHistory] = useState<BuildHistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [pipelineName, setPipelineName] = useState<string>('');

  useEffect(() => {
    const fetchBuildHistory = async () => {
      if (!pipelineId) return;
      
      try {
        setLoading(true);
        const response = await getBuildHistory(pipelineId);
        setBuildHistory(response.data.items);
        
        // Set pipeline name from the first build if available
        if (response.data.items.length > 0) {
          setPipelineName(`Pipeline #${pipelineId}`);
        }
      } catch (err) {
        console.error('Error fetching build history:', err);
        setError('Failed to load build history. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchBuildHistory();
  }, [pipelineId]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle color="success" />;
      case 'failure':
        return <Cancel color="error" />;
      case 'in_progress':
        return <HourglassEmpty color="primary" />;
      default:
        return null;
    }
  };

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Header />
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Build History for {pipelineName}
        </Typography>
        <Link to="/" style={{ textDecoration: 'none' }}>
          ← Back to Dashboard
        </Link>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Typography color="error">{error}</Typography>
      ) : buildHistory.length === 0 ? (
        <Typography>No build history available for this pipeline.</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Build #</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Commit</TableCell>
                <TableCell>Triggered By</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {buildHistory.map((build) => (
                <TableRow key={build.id}>
                  <TableCell>{build.build_number}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getStatusIcon(build.status)}
                      <Typography>{build.status}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    {format(new Date(build.timestamp), 'MMM dd, yyyy HH:mm')}
                  </TableCell>
                  <TableCell>{formatDuration(build.duration)}</TableCell>
                  <TableCell>
                    <Chip 
                      label={build.commit_hash.substring(0, 7)} 
                      size="small" 
                      color="primary" 
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{build.triggered_by}</TableCell>
                  <TableCell>
                    <Link to={`/logs/${build.pipeline_id}/${build.id}`}>
                      View Logs
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default BuildHistoryPage; 
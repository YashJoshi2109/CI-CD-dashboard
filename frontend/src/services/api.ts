import axios from 'axios';
import { PipelineStatus, BuildLog, ApiResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getPipelineStatus = async (): Promise<ApiResponse<PipelineStatus[]>> => {
    try {
        const response = await api.get('/pipeline-status');
        return response.data;
    } catch (error) {
        console.error('Error fetching pipeline status:', error);
        throw error;
    }
};

export const getBuildLogs = async (pipelineId: string): Promise<ApiResponse<BuildLog[]>> => {
    try {
        const response = await api.get(`/build-logs/${pipelineId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching build logs:', error);
        throw error;
    }
};

export const triggerRollback = async (pipelineId: string): Promise<ApiResponse<null>> => {
    try {
        const response = await api.post(`/trigger-rollback/${pipelineId}`);
        return response.data;
    } catch (error) {
        console.error('Error triggering rollback:', error);
        throw error;
    }
}; 
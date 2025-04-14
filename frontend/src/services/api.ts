import axios from 'axios';
import { PipelineStatus, BuildLog, ApiResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getPipelineStatus = async (): Promise<ApiResponse<PipelineStatus[]>> => {
    try {
        const response = await api.get('/api/pipeline-status');
        return {
            data: response.data,
            message: 'Pipeline status fetched successfully'
        };
    } catch (error) {
        console.error('Error fetching pipeline status:', error);
        return {
            data: [],
            message: error instanceof Error ? error.message : 'Unknown error occurred',
            error: 'Failed to fetch pipeline status'
        };
    }
};

export const getPipelineStatuses = async (): Promise<ApiResponse<PipelineStatus[]>> => {
    try {
        console.log('Fetching pipeline statuses...');
        const response = await api.get('/api/pipeline-status');
        console.log('Pipeline statuses response:', response.data);
        
        if (!Array.isArray(response.data)) {
            console.error('Invalid response format - expected array:', response.data);
            return {
                data: [],
                message: 'Invalid response format from server',
                error: 'Response data is not an array'
            };
        }

        const pipelines = response.data.map(pipeline => ({
            ...pipeline,
            status: pipeline.status.toLowerCase(),
            last_build_time: new Date(pipeline.last_build_time).toISOString()
        }));

        console.log('Transformed pipelines:', pipelines);
        return {
            data: pipelines,
            message: 'Pipeline statuses fetched successfully'
        };
    } catch (error) {
        console.error('Error fetching pipeline statuses:', error);
        if (axios.isAxiosError(error)) {
            console.error('Axios error details:', {
                status: error.response?.status,
                data: error.response?.data,
                config: {
                    url: error.config?.url,
                    method: error.config?.method,
                    baseURL: error.config?.baseURL
                }
            });
        }
        return {
            data: [],
            message: error instanceof Error ? error.message : 'Unknown error occurred',
            error: 'Failed to fetch pipeline statuses'
        };
    }
};

export const getBuildLogs = async (pipelineId: string): Promise<ApiResponse<BuildLog[]>> => {
    try {
        const response = await api.get(`/api/build-logs/${pipelineId}`);
        return {
            data: response.data,
            message: 'Build logs fetched successfully'
        };
    } catch (error) {
        console.error('Error fetching build logs:', error);
        return {
            data: [],
            message: error instanceof Error ? error.message : 'Unknown error occurred',
            error: 'Failed to fetch build logs'
        };
    }
};

export const triggerRollback = async (pipelineId: string): Promise<ApiResponse<void>> => {
    try {
        const response = await api.post(`/api/trigger-rollback/${pipelineId}`);
        return {
            data: undefined,
            message: response.data.message || 'Rollback triggered successfully'
        };
    } catch (error) {
        console.error('Error triggering rollback:', error);
        return {
            data: undefined,
            message: error instanceof Error ? error.message : 'Unknown error occurred',
            error: 'Failed to trigger rollback'
        };
    }
};

export const triggerBuild = async (pipelineId: string): Promise<ApiResponse<void>> => {
    try {
        const response = await api.post(`/api/trigger-build/${pipelineId}`);
        return {
            data: undefined,
            message: response.data.message || 'Build triggered successfully'
        };
    } catch (error) {
        console.error('Error triggering build:', error);
        return {
            data: undefined,
            message: error instanceof Error ? error.message : 'Unknown error occurred',
            error: 'Failed to trigger build'
        };
    }
};

export const getBuildHistory = async (pipelineId: string): Promise<ApiResponse<any>> => {
    try {
        const response = await api.get(`/api/build-history/${pipelineId}`);
        return {
            data: response.data,
            message: 'Build history fetched successfully'
        };
    } catch (error) {
        console.error('Error fetching build history:', error);
        return {
            data: null,
            message: error instanceof Error ? error.message : 'Unknown error occurred',
            error: 'Failed to fetch build history'
        };
    }
}; 
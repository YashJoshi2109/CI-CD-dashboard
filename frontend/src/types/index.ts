export interface PipelineStatus {
    id: string;
    name: string;
    status: 'success' | 'failure' | 'in_progress';
    last_build_time: string;
    duration?: number; // in seconds
    commit_hash?: string;
}

export interface BuildLog {
    id: string;
    pipeline_id: string;
    log_content: string;
    timestamp: string;
    status: 'success' | 'failure' | 'in_progress';
}

export interface ApiResponse<T> {
    data: T;
    message: string;
    error?: string;
}

export interface BuildHistoryItem {
    id: string;
    pipeline_id: string;
    build_number: number;
    commit_hash: string;
    status: 'success' | 'failure' | 'in_progress';
    timestamp: string;
    duration: number; // in seconds
    triggered_by: string;
}

export interface BuildHistoryResponse {
    items: BuildHistoryItem[];
    total_count: number;
} 
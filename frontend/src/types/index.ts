export interface PipelineStatus {
    id: string;
    name: string;
    status: string;
    last_build_time: string;
    duration?: string;
    commit_hash?: string;
}

export interface BuildLog {
    id: string;
    pipeline_id: string;
    log_content: string;
    timestamp: string;
    status: string;
}

export interface ApiResponse<T> {
    data: T;
    message?: string;
    error?: string;
} 
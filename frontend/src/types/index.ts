export interface PipelineStatus {
    id: string;
    name: string;
    status: string;
    last_build_time: string;
    duration?: string;
    commit_hash?: string;
    url?: string;
    building?: boolean;
    number?: number;
    error?: string;
}

export interface BuildLog {
    id: string;
    pipeline_id: string;
    build_number: number;
    log_content: string;
    timestamp: string;
    status: string;
}

export interface ApiResponse<T> {
    data: T;
    message: string;
    error?: string;
}

export interface BuildHistoryItem {
    number: number;
    result: string;
    timestamp: string;
    duration: number;
    url: string;
    commit_hash?: string;
    commit_message?: string;
}

export interface BuildHistoryResponse {
    items: BuildHistoryItem[];
    total_count: number;
} 
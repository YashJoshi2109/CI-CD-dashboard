from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any, ForwardRef


class PipelineBase(BaseModel):
    name: str
    status: str
    last_build_time: datetime
    duration: Optional[str] = None
    commit_hash: Optional[str] = None
    url: Optional[str] = None
    last_build_number: Optional[int] = None
    description: Optional[str] = None


class PipelineCreate(PipelineBase):
    pass


class BuildLogBase(BaseModel):
    log_content: str
    timestamp: datetime
    status: str
    build_number: int
    duration: Optional[str] = None
    commit_hash: Optional[str] = None
    commit_message: Optional[str] = None


class BuildLogCreate(BuildLogBase):
    pipeline_id: str


class BuildLog(BuildLogBase):
    id: str
    pipeline_id: str

    class Config:
        from_attributes = True


class Pipeline(PipelineBase):
    id: str
    build_logs: List["BuildLog"] = []

    class Config:
        from_attributes = True


class RollbackResponse(BaseModel):
    message: str
    pipeline_name: str
    timestamp: datetime = datetime.utcnow()


class BuildTriggerResponse(BaseModel):
    message: str
    pipeline_name: str
    parameters: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()


class JenkinsJob(BaseModel):
    name: str
    url: str
    color: str


class JenkinsJobList(BaseModel):
    jobs: List[JenkinsJob]
    count: int


class JenkinsStatus(BaseModel):
    connected: bool
    message: str


class BuildHistoryItem(BaseModel):
    number: int
    result: str
    timestamp: datetime
    duration: float
    url: str
    commit_hash: Optional[str] = None
    commit_message: Optional[str] = None


class BuildHistory(BaseModel):
    pipeline_id: str
    pipeline_name: str
    builds: List[BuildHistoryItem]
    count: int


Pipeline.update_forward_refs()

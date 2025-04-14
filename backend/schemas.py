from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class PipelineBase(BaseModel):
    name: str
    status: str
    last_build_time: datetime
    duration: Optional[str] = None
    commit_hash: Optional[str] = None


class PipelineCreate(PipelineBase):
    pass


class Pipeline(PipelineBase):
    id: str
    build_logs: List["BuildLog"] = []

    class Config:
        orm_mode = True


class BuildLogBase(BaseModel):
    log_content: str
    timestamp: datetime
    status: str


class BuildLogCreate(BuildLogBase):
    pipeline_id: str


class BuildLog(BuildLogBase):
    id: str
    pipeline_id: str

    class Config:
        orm_mode = True


class RollbackResponse(BaseModel):
    message: str
    pipeline_name: str
    timestamp: datetime = datetime.utcnow()


Pipeline.update_forward_refs()

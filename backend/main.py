from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from models import Pipeline, BuildLog, get_db
from database import init_db
from schemas import Pipeline as PipelineSchema, BuildLog as BuildLogSchema, RollbackResponse
from services.jenkins_service import JenkinsService

# Initialize database
init_db()

app = FastAPI(
    title="CI/CD Dashboard API",
    description="API for monitoring and managing CI/CD pipelines",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Jenkins service
jenkins_service = JenkinsService()


@app.get("/")
async def root():
    return {"message": "Welcome to CI/CD Dashboard API"}


@app.get("/api/pipeline-status", response_model=List[PipelineSchema])
async def get_pipeline_status(db: Session = Depends(get_db)):
    try:
        # Get all pipelines from database
        pipelines = db.query(Pipeline).all()

        # Update pipeline status from Jenkins
        for pipeline in pipelines:
            try:
                # Get latest status from Jenkins
                status_info = jenkins_service.get_pipeline_status(
                    pipeline.name)

                # Update pipeline information
                pipeline.status = status_info["status"]
                pipeline.last_build_time = status_info["last_build_time"]
                pipeline.duration = status_info["duration"]
                pipeline.commit_hash = status_info["commit_hash"]

                # Get and save build log if available
                job_info = jenkins_service.get_job_info(pipeline.name)
                if job_info and job_info.get("lastBuild"):
                    build_number = job_info["lastBuild"]["number"]
                    build_log = jenkins_service.get_build_console_output(
                        pipeline.name, build_number)

                    if build_log:
                        log = BuildLog(
                            id=str(uuid.uuid4()),
                            pipeline_id=pipeline.id,
                            log_content=build_log,
                            timestamp=status_info["last_build_time"],
                            status=status_info["status"]
                        )
                        db.add(log)

            except Exception as e:
                print(f"Error updating pipeline {pipeline.name}: {str(e)}")

        db.commit()
        return pipelines
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pipeline status: {str(e)}"
        )


@app.get("/api/build-logs/{pipeline_id}", response_model=List[BuildLogSchema])
async def get_build_logs(pipeline_id: str, db: Session = Depends(get_db)):
    try:
        # Verify pipeline exists
        pipeline = db.query(Pipeline).filter(
            Pipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pipeline not found"
            )

        # Get logs from database
        logs = db.query(BuildLog).filter(
            BuildLog.pipeline_id == pipeline_id).all()
        return logs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch build logs: {str(e)}"
        )


@app.post("/api/trigger-rollback/{pipeline_id}", response_model=RollbackResponse)
async def trigger_rollback(pipeline_id: str, db: Session = Depends(get_db)):
    try:
        # Verify pipeline exists
        pipeline = db.query(Pipeline).filter(
            Pipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pipeline not found"
            )

        # Trigger rollback in Jenkins
        success = jenkins_service.trigger_rollback(pipeline.name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to trigger rollback"
            )

        return RollbackResponse(
            message="Rollback triggered successfully",
            pipeline_name=pipeline.name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger rollback: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
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


@app.get("/api/jenkins/status")
@app.get("/jenkins/status")
async def jenkins_status():
    """Check the status of the Jenkins connection"""
    is_connected = jenkins_service.check_connection()
    return {
        "connected": is_connected,
        "message": "Successfully connected to Jenkins" if is_connected else "Failed to connect to Jenkins"
    }


@app.get("/api/jenkins/jobs")
@app.get("/jenkins/jobs")
async def get_jenkins_jobs():
    """List all jobs/pipelines from Jenkins"""
    jobs = jenkins_service.get_all_jobs()
    return {"jobs": jobs, "count": len(jobs)}


@app.get("/api/pipeline-status", response_model=List[PipelineSchema])
@app.get("/api/pipeline-statuses", response_model=List[PipelineSchema])
@app.get("/pipeline-status", response_model=List[PipelineSchema])
@app.get("/pipeline-statuses", response_model=List[PipelineSchema])
async def get_pipeline_status(db: Session = Depends(get_db)):
    try:
        # Get all pipelines from database
        pipelines = db.query(Pipeline).all()

        # If there are no pipelines yet, try to fetch them from Jenkins
        if not pipelines:
            jobs = jenkins_service.get_all_jobs()
            for job in jobs:
                pipeline = Pipeline(
                    id=str(uuid.uuid4()),
                    name=job["name"],
                    status="UNKNOWN",
                    last_build_time=datetime.utcnow()
                )
                db.add(pipeline)
            db.commit()
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
                pipeline.url = status_info.get("url")
                pipeline.last_build_number = status_info.get("number")

                # Get and save build log if available
                job_info = jenkins_service.get_job_info(pipeline.name)
                if job_info and job_info.get("lastBuild"):
                    build_number = job_info["lastBuild"]["number"]
                    build_log = jenkins_service.get_build_console_output(
                        pipeline.name, build_number)

                    if build_log:
                        # Check if this build log already exists
                        existing_log = db.query(BuildLog).filter(
                            BuildLog.pipeline_id == pipeline.id,
                            BuildLog.build_number == build_number
                        ).first()

                        if not existing_log:
                            log = BuildLog(
                                id=str(uuid.uuid4()),
                                pipeline_id=pipeline.id,
                                build_number=build_number,
                                # Limit log content size
                                log_content=build_log[:10000],
                                timestamp=status_info["last_build_time"],
                                status=status_info["status"]
                            )
                            db.add(log)

            except Exception as e:
                print(f"Error updating pipeline {pipeline.name}: {str(e)}")
                continue

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
        logs = db.query(BuildLog).filter(BuildLog.pipeline_id ==
                                         pipeline_id).order_by(BuildLog.timestamp.desc()).all()
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


@app.post("/api/trigger-build/{pipeline_id}")
async def trigger_build(pipeline_id: str, parameters: Optional[Dict[str, Any]] = None, db: Session = Depends(get_db)):
    try:
        # Verify pipeline exists
        pipeline = db.query(Pipeline).filter(
            Pipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pipeline not found"
            )

        # Trigger build in Jenkins
        success = jenkins_service.trigger_build(pipeline.name, parameters)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to trigger build"
            )

        return {
            "message": "Build triggered successfully",
            "pipeline_name": pipeline.name,
            "parameters": parameters,
            "timestamp": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger build: {str(e)}"
        )


@app.get("/api/build-history/{pipeline_id}")
async def get_build_history(pipeline_id: str, limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    try:
        # Verify pipeline exists
        pipeline = db.query(Pipeline).filter(
            Pipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pipeline not found"
            )

        # Get build history from Jenkins
        history = jenkins_service.get_build_history(pipeline.name, limit)

        return {
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline.name,
            "builds": history,
            "count": len(history)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch build history: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

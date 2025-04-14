import jenkins
import os
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class JenkinsService:
    def __init__(self):
        self.server = jenkins.Jenkins(
            os.getenv("JENKINS_URL", "http://localhost:8080"),
            username=os.getenv("JENKINS_USERNAME", "admin"),
            password=os.getenv("JENKINS_PASSWORD", "admin")
        )

    def get_job_info(self, job_name: str) -> Optional[Dict[str, Any]]:
        try:
            return self.server.get_job_info(job_name)
        except jenkins.JenkinsException as e:
            print(f"Error getting job info for {job_name}: {str(e)}")
            return None

    def get_build_info(self, job_name: str, build_number: int) -> Optional[Dict[str, Any]]:
        try:
            return self.server.get_build_info(job_name, build_number)
        except jenkins.JenkinsException as e:
            print(
                f"Error getting build info for {job_name} #{build_number}: {str(e)}")
            return None

    def get_build_console_output(self, job_name: str, build_number: int) -> Optional[str]:
        try:
            return self.server.get_build_console_output(job_name, build_number)
        except jenkins.JenkinsException as e:
            print(
                f"Error getting console output for {job_name} #{build_number}: {str(e)}")
            return None

    def trigger_rollback(self, job_name: str) -> bool:
        try:
            rollback_job_name = f"{job_name}-rollback"
            self.server.build_job(rollback_job_name)
            return True
        except jenkins.JenkinsException as e:
            print(f"Error triggering rollback for {job_name}: {str(e)}")
            return False

    def get_pipeline_status(self, job_name: str) -> Dict[str, Any]:
        job_info = self.get_job_info(job_name)
        if not job_info:
            return {
                "status": "unknown",
                "last_build_time": datetime.utcnow(),
                "duration": None,
                "commit_hash": None
            }

        last_build = job_info.get("lastBuild")
        if not last_build:
            return {
                "status": "unknown",
                "last_build_time": datetime.utcnow(),
                "duration": None,
                "commit_hash": None
            }

        build_info = self.get_build_info(job_name, last_build["number"])
        commit_hash = build_info.get("changeSet", {}).get("items", [{}])[
            0].get("commitId") if build_info else None

        return {
            "status": last_build.get("result", "unknown"),
            "last_build_time": datetime.fromtimestamp(last_build.get("timestamp", 0) / 1000),
            "duration": f"{last_build.get('duration', 0) / 1000}s",
            "commit_hash": commit_hash
        }

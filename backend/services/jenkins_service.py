import os
import time
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()


class JenkinsService:
    def __init__(self):
        # Get Jenkins configuration from environment variables
        self.jenkins_url = os.getenv("JENKINS_URL", "http://localhost:8080")
        self.jenkins_user = os.getenv("JENKINS_USERNAME", "admin")
        self.jenkins_password = os.getenv("JENKINS_PASSWORD", "admin")

        # Initialize connection properties
        self.session = requests.Session()
        self.session.auth = (self.jenkins_user, self.jenkins_password)
        self.is_connected = self.check_connection()

        print(f"Jenkins Service initialized with URL: {self.jenkins_url}")
        print(
            f"Connection status: {'CONNECTED' if self.is_connected else 'DISCONNECTED'}")

    def check_connection(self) -> bool:
        """Check if the connection to Jenkins is working."""
        try:
            print(f"Checking connection to Jenkins at {self.jenkins_url}")
            response = self.session.get(
                f"{self.jenkins_url}/api/json", timeout=10)
            response.raise_for_status()  # Raise exception for non-200 responses

            data = response.json()
            print(f"Connected to Jenkins: {data.get('nodeName', 'Unknown')}")

            # Try to get user info
            user_response = self.session.get(
                f"{self.jenkins_url}/me/api/json", timeout=10)
            if user_response.status_code == 200:
                user_data = user_response.json()
                print(
                    f"Authenticated as: {user_data.get('fullName', 'Unknown')}")

            return True
        except Exception as e:
            print(f"Jenkins connection test failed: {str(e)}")
            print(f"Exception type: {type(e)}")
            return False

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get a list of all jobs (pipelines) from Jenkins."""
        try:
            if not self.is_connected:
                print("Not connected to Jenkins. Trying to reconnect...")
                self.is_connected = self.check_connection()
                if not self.is_connected:
                    return []

            print(f"Fetching all jobs from {self.jenkins_url}/api/json")
            response = self.session.get(
                f"{self.jenkins_url}/api/json", timeout=10)
            response.raise_for_status()

            data = response.json()
            jobs = data.get('jobs', [])
            print(f"Successfully retrieved {len(jobs)} jobs from Jenkins")

            return [
                {
                    "name": job["name"],
                    "url": job["url"],
                    # blue=success, red=failed, etc.
                    "color": job.get("color", "unknown")
                }
                for job in jobs
            ]
        except Exception as e:
            print(f"Error getting all jobs: {str(e)}")
            return []

    def get_pipeline_status(self, job_name: str) -> Dict[str, Any]:
        """Get detailed status information for a specific pipeline."""
        try:
            if not self.is_connected:
                self.is_connected = self.check_connection()
                if not self.is_connected:
                    return {
                        "status": "ERROR",
                        "last_build_time": datetime.utcnow(),
                        "duration": "0s",
                        "commit_hash": None,
                        "error": "Not connected to Jenkins"
                    }

            # Get job info
            job_info_response = self.session.get(
                f"{self.jenkins_url}/job/{job_name}/api/json", timeout=10)
            job_info_response.raise_for_status()
            job_info = job_info_response.json()

            # Handle case where job exists but has no builds
            if not job_info.get("lastBuild"):
                return {
                    "status": "NONE",
                    "last_build_time": datetime.utcnow(),
                    "duration": "0s",
                    "commit_hash": None
                }

            # Get the last build information
            last_build_number = job_info["lastBuild"]["number"]
            build_info_response = self.session.get(
                f"{self.jenkins_url}/job/{job_name}/{last_build_number}/api/json", timeout=10)
            build_info_response.raise_for_status()
            build_info = build_info_response.json()

            # Get commit hash if available
            commit_hash = None
            if build_info.get("actions"):
                for action in build_info["actions"]:
                    if action.get("lastBuiltRevision"):
                        commit_hash = action["lastBuiltRevision"]["SHA1"]
                        break

            # Calculate duration in a human-readable format
            duration_seconds = build_info["duration"] / 1000
            if duration_seconds < 60:
                duration = f"{duration_seconds:.1f}s"
            else:
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                duration = f"{minutes}m {seconds}s"

            return {
                "status": build_info.get("result", "UNKNOWN"),
                "last_build_time": datetime.fromtimestamp(build_info["timestamp"] / 1000),
                "duration": duration,
                "commit_hash": commit_hash,
                "url": build_info["url"],
                "building": build_info.get("building", False),
                "number": last_build_number
            }
        except Exception as e:
            print(f"Error getting pipeline status for {job_name}: {str(e)}")
            return {
                "status": "ERROR",
                "last_build_time": datetime.utcnow(),
                "duration": "0s",
                "commit_hash": None,
                "error": str(e)
            }

    def get_job_info(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a Jenkins job."""
        try:
            if not self.is_connected:
                self.is_connected = self.check_connection()
                if not self.is_connected:
                    return None

            response = self.session.get(
                f"{self.jenkins_url}/job/{job_name}/api/json", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting job info for {job_name}: {str(e)}")
            return None

    def get_build_console_output(self, job_name: str, build_number: int) -> Optional[str]:
        """Get the console output of a specific build."""
        try:
            if not self.is_connected:
                self.is_connected = self.check_connection()
                if not self.is_connected:
                    return None

            response = self.session.get(
                f"{self.jenkins_url}/job/{job_name}/{build_number}/consoleText", timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(
                f"Error getting console output for {job_name} #{build_number}: {str(e)}")
            return None

    def trigger_build(self, job_name: str, parameters: Optional[Dict[str, Any]] = None) -> bool:
        """Trigger a build for a specific job with optional parameters."""
        try:
            if not self.is_connected:
                self.is_connected = self.check_connection()
                if not self.is_connected:
                    return False

            url = f"{self.jenkins_url}/job/{job_name}/build"
            if parameters:
                url = f"{self.jenkins_url}/job/{job_name}/buildWithParameters"
                response = self.session.post(url, data=parameters, timeout=10)
            else:
                response = self.session.post(url, timeout=10)

            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error triggering build for {job_name}: {str(e)}")
            return False

    def trigger_rollback(self, job_name: str) -> bool:
        """Trigger a rollback for a specific pipeline."""
        try:
            if not self.is_connected:
                self.is_connected = self.check_connection()
                if not self.is_connected:
                    return False

            # Check if there's a specific rollback job
            rollback_job_name = f"{job_name}-rollback"
            try:
                response = self.session.get(
                    f"{self.jenkins_url}/job/{rollback_job_name}/api/json", timeout=5)
                if response.status_code == 200:
                    # Use the dedicated rollback job
                    return self.trigger_build(rollback_job_name)
            except:
                pass

            # Trigger the original job with a rollback parameter
            return self.trigger_build(job_name, {"action": "rollback"})
        except Exception as e:
            print(f"Error triggering rollback for {job_name}: {str(e)}")
            return False

    def get_build_history(self, job_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the build history for a specific job."""
        try:
            if not self.is_connected:
                self.is_connected = self.check_connection()
                if not self.is_connected:
                    return []

            # Get job info with builds
            response = self.session.get(
                f"{self.jenkins_url}/job/{job_name}/api/json?tree=builds[number,result,timestamp,duration,url]", timeout=10)
            response.raise_for_status()
            job_info = response.json()

            builds = job_info.get("builds", [])[:limit]
            history = []

            for build in builds:
                build_number = build["number"]

                # Get more detailed build info
                build_response = self.session.get(
                    f"{self.jenkins_url}/job/{job_name}/{build_number}/api/json", timeout=10)
                if build_response.status_code != 200:
                    continue

                build_info = build_response.json()

                # Extract commit info if available
                commit_hash = None
                commit_message = None
                if build_info.get("actions"):
                    for action in build_info["actions"]:
                        if action.get("lastBuiltRevision"):
                            commit_hash = action["lastBuiltRevision"]["SHA1"]
                        if action.get("buildsByBranchName"):
                            for branch, branch_build in action["buildsByBranchName"].items():
                                if branch_build.get("marked"):
                                    commit_message = branch_build["marked"].get(
                                        "message")

                history.append({
                    "number": build_number,
                    "result": build_info.get("result", "UNKNOWN"),
                    "timestamp": datetime.fromtimestamp(build_info["timestamp"] / 1000),
                    "duration": build_info["duration"] / 1000,  # in seconds
                    "url": build_info["url"],
                    "commit_hash": commit_hash,
                    "commit_message": commit_message
                })

            return history
        except Exception as e:
            print(f"Error getting build history for {job_name}: {str(e)}")
            return []

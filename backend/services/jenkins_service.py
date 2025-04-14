import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()


class JenkinsService:
    def __init__(self):
        # Get Jenkins configuration from environment variables
        self.jenkins_url = os.getenv("JENKINS_URL", "http://localhost:8081")
        self.jenkins_user = os.getenv("JENKINS_USERNAME", "admin")
        self.jenkins_password = os.getenv("JENKINS_PASSWORD", "admin")

        # Initialize connection properties
        self.session = requests.Session()
        self.session.auth = (self.jenkins_user, self.jenkins_password)
        self.timeout = 30.0  # Set a reasonable timeout value

        print(f"Attempting to connect to Jenkins at: {self.jenkins_url}")
        print(
            f"Using credentials - Username: {self.jenkins_user}, Password: {'*****' if self.jenkins_password else 'Not set'}")

        self.is_connected = self.check_connection()
        print(f"Jenkins Service initialized with URL: {self.jenkins_url}")
        print(
            f"Connection status: {'CONNECTED' if self.is_connected else 'DISCONNECTED'}")

    def check_connection(self) -> bool:
        """Check if the connection to Jenkins is working."""
        try:
            # Try to get basic server info first
            print("Testing Jenkins connection...")
            api_url = f"{self.jenkins_url}/api/json"
            print(f"Making request to: {api_url}")

            response = self.session.get(api_url, timeout=self.timeout)
            print(f"Response status code: {response.status_code}")

            if response.status_code == 403:
                print("Authentication failed. Please check your Jenkins credentials.")
                return False

            response.raise_for_status()
            server_data = response.json()
            print(f"Server info: {server_data.get('nodeName', 'Unknown')}")

            # Try to get authenticated user info
            whoami_url = f"{self.jenkins_url}/me/api/json"
            print(f"Checking authentication with: {whoami_url}")

            user_response = self.session.get(whoami_url, timeout=self.timeout)
            print(f"Auth check status code: {user_response.status_code}")

            user_response.raise_for_status()
            user_data = user_response.json()

            print(
                f"Connected to Jenkins: {server_data.get('nodeName', 'Unknown')}")
            print(f"Authenticated as: {user_data.get('fullName', 'Unknown')}")

            return True
        except requests.exceptions.ConnectionError as e:
            print(
                f"Connection error: Could not connect to Jenkins at {self.jenkins_url}")
            print(f"Error details: {str(e)}")
            return False
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {str(e)}")
            print(
                f"Response content: {e.response.text if hasattr(e, 'response') else 'No response content'}")
            return False
        except Exception as e:
            print(f"Jenkins connection test failed: {str(e)}")
            return False

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all Jenkins jobs."""
        if not self.is_connected:
            print("Not connected to Jenkins")
            return []

        try:
            print(f"Fetching all jobs from {self.jenkins_url}/api/json")
            response = self.session.get(
                f"{self.jenkins_url}/api/json", timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            jobs = data.get('jobs', [])
            print(f"Successfully retrieved {len(jobs)} jobs from Jenkins")

            # Transform the jobs data into the format expected by the frontend
            formatted_jobs = [
                {
                    "id": job["name"],  # Use job name as ID
                    "name": job["name"],
                    "url": job["url"],
                    "status": self._get_job_status(job.get("color", "unknown")),
                    "lastBuildTime": None,  # Will be updated with actual build info
                    "lastBuildDuration": None,  # Will be updated with actual build info
                    "lastCommitHash": None  # Will be updated with actual build info
                }
                for job in jobs
            ]

            # Update each job with its latest build information
            for job in formatted_jobs:
                job_info = self.get_job_info(job["name"])
                if job_info and job_info.get("lastBuild"):
                    last_build = self.get_build_info(
                        job["name"], job_info["lastBuild"]["number"])
                    if last_build:
                        job["lastBuildTime"] = last_build.get("timestamp")
                        job["lastBuildDuration"] = last_build.get("duration")
                        # Try to get commit hash from build actions
                        for action in last_build.get("actions", []):
                            if action.get("lastBuiltRevision"):
                                job["lastCommitHash"] = action["lastBuiltRevision"].get(
                                    "SHA1")
                                break

            return formatted_jobs
        except Exception as e:
            print(f"Error fetching jobs: {str(e)}")
            return []

    def _get_job_status(self, color: str) -> str:
        """Convert Jenkins color status to frontend status."""
        status_map = {
            "blue": "SUCCESS",
            "red": "FAILURE",
            "yellow": "UNSTABLE",
            "grey": "NOT_BUILT",
            "disabled": "DISABLED",
            "notbuilt": "NOT_BUILT",
            "aborted": "ABORTED"
        }
        if color.endswith("_anime"):
            return "BUILDING"
        return status_map.get(color, "UNKNOWN")

    def get_job_info(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific job."""
        if not self.is_connected:
            return None

        try:
            url = f"{self.jenkins_url}/job/{job_name}/api/json"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching job info for {job_name}: {str(e)}")
            return None

    def get_build_info(self, job_name: str, build_number: int) -> Optional[Dict[str, Any]]:
        """Get information about a specific build."""
        if not self.is_connected:
            return None

        try:
            url = f"{self.jenkins_url}/job/{job_name}/{build_number}/api/json"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(
                f"Error fetching build info for {job_name} #{build_number}: {str(e)}")
            return None

    def trigger_build(self, job_name: str) -> bool:
        """Trigger a build for a specific job."""
        if not self.is_connected:
            return False

        try:
            url = f"{self.jenkins_url}/job/{job_name}/build"
            response = self.session.post(url, timeout=self.timeout)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error triggering build for {job_name}: {str(e)}")
            return False

    def get_build_console_output(self, job_name: str, build_number: int) -> str:
        """Get console output for a specific build."""
        if not self.is_connected:
            return ""

        try:
            url = f"{self.jenkins_url}/job/{job_name}/{build_number}/consoleText"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(
                f"Error fetching console output for {job_name} #{build_number}: {str(e)}")
            return ""

    def get_pipeline_status(self, job_name: str) -> Dict[str, Any]:
        """Get detailed status information for a specific pipeline."""
        try:
            if not self.is_connected:
                print("Not connected to Jenkins")
                return {
                    "status": "UNKNOWN",
                    "last_build_time": datetime.utcnow(),
                    "duration": "0s",
                    "commit_hash": None,
                    "error": "Not connected to Jenkins"
                }

            # Get job info
            print(f"Fetching job info for {job_name}")
            job_info = self.get_job_info(job_name)

            if not job_info:
                print(f"No job info found for {job_name}")
                return {
                    "status": "UNKNOWN",
                    "last_build_time": datetime.utcnow(),
                    "duration": "0s",
                    "commit_hash": None,
                    "error": f"No job info found for {job_name}"
                }

            # Handle case where job exists but has no builds
            if not job_info.get("lastBuild"):
                print(f"No builds found for {job_name}")
                return {
                    "status": "NOT_BUILT",
                    "last_build_time": datetime.utcnow(),
                    "duration": "0s",
                    "commit_hash": None
                }

            # Get the last build information
            last_build_number = job_info["lastBuild"]["number"]
            print(f"Fetching build info for {job_name} #{last_build_number}")
            build_info = self.get_build_info(job_name, last_build_number)

            if not build_info:
                print(
                    f"No build info found for {job_name} #{last_build_number}")
                return {
                    "status": "UNKNOWN",
                    "last_build_time": datetime.utcnow(),
                    "duration": "0s",
                    "commit_hash": None,
                    "error": f"No build info found for {job_name} #{last_build_number}"
                }

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

            status = build_info.get("result", "UNKNOWN")
            if build_info.get("building"):
                status = "BUILDING"

            return {
                "status": status,
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

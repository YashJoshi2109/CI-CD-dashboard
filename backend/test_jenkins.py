#!/usr/bin/env python
"""
Test script for Jenkins service connectivity and functions.
This script can be used to test the Jenkins API integration without needing the full application.
"""

import os
from dotenv import load_dotenv
from services.jenkins_service import JenkinsService
import json
from datetime import datetime

# Load environment variables
load_dotenv()


def format_json(data):
    """Format JSON data for pretty printing"""
    return json.dumps(data, indent=2, default=str)


def main():
    print("=== Jenkins Connection Test ===")
    print(f"JENKINS_URL: {os.getenv('JENKINS_URL', 'Not set')}")
    print(f"JENKINS_USERNAME: {os.getenv('JENKINS_USERNAME', 'Not set')}")
    print(
        f"JENKINS_PASSWORD: {'*****' if os.getenv('JENKINS_PASSWORD') else 'Not set'}")
    print("\nInitializing Jenkins service...")

    jenkins_service = JenkinsService()

    print("\nTesting connection...")
    if jenkins_service.check_connection():
        print("✅ Connection successful!")

        print("\nFetching all jobs...")
        jobs = jenkins_service.get_all_jobs()
        print(f"Found {len(jobs)} jobs:")
        print(format_json(jobs))

        if len(jobs) > 0:
            # Pick the first job for further testing
            test_job = jobs[0]["name"]
            print(f"\nTesting pipeline status for job: {test_job}")
            status = jenkins_service.get_pipeline_status(test_job)
            print(format_json(status))

            print(f"\nFetching build history for job: {test_job}")
            history = jenkins_service.get_build_history(test_job, limit=5)
            print(format_json(history))

            if status.get("number"):
                print(
                    f"\nFetching console output for job: {test_job}, build: {status['number']}")
                console_output = jenkins_service.get_build_console_output(
                    test_job, status["number"])
                if console_output:
                    print(
                        f"Console output length: {len(console_output)} characters")
                    print("First 200 characters:")
                    print(console_output[:200])
                else:
                    print("❌ Failed to get console output")
    else:
        print("❌ Connection failed!")
        print("Please check your Jenkins credentials and URL.")
        print("If you don't have a Jenkins server, you can use the mock implementation for development.")


if __name__ == "__main__":
    main()

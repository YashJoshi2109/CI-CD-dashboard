from main import app
import pytest
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to path so we can import the main app
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


client = TestClient(app)


@pytest.fixture
def mock_jenkins_service():
    with patch('services.jenkins_service.JenkinsService') as mock:
        instance = mock.return_value

        # Mock pipeline status
        instance.get_pipeline_status.return_value = {
            "status": "success",
            "last_build_time": "2023-01-01T12:00:00",
            "duration": "30s",
            "commit_hash": "abc123"
        }

        # Mock job info
        instance.get_job_info.return_value = {
            "lastBuild": {"number": 1}
        }

        # Mock build info
        instance.get_build_info.return_value = {
            "timestamp": 1640995200000,
            "duration": 30000
        }

        # Mock console output
        instance.get_build_console_output.return_value = "Build log output"

        # Mock rollback
        instance.trigger_rollback.return_value = True

        yield instance


@pytest.fixture
def mock_db_session():
    with patch('models.get_db') as mock_db:
        session = MagicMock()
        mock_db.return_value.__next__.return_value = session
        yield session


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to CI/CD Dashboard API"}


@patch('main.jenkins_service')
def test_get_pipeline_status(mock_jenkins, mock_db_session):
    # Mock the database query result
    pipeline = MagicMock()
    pipeline.id = "test-id"
    pipeline.name = "test-pipeline"
    mock_db_session.query.return_value.all.return_value = [pipeline]

    # Mock the jenkins service
    mock_jenkins.get_pipeline_status.return_value = {
        "status": "success",
        "last_build_time": "2023-01-01T12:00:00",
        "duration": "30s",
        "commit_hash": "abc123"
    }
    mock_jenkins.get_job_info.return_value = {"lastBuild": {"number": 1}}
    mock_jenkins.get_build_console_output.return_value = "Test log"

    response = client.get("/api/pipeline-status")
    assert response.status_code == 200
    mock_db_session.commit.assert_called_once()


@patch('main.jenkins_service')
def test_get_build_logs(mock_jenkins, mock_db_session):
    # Mock pipeline existence check
    mock_db_session.query.return_value.filter.return_value.first.return_value = MagicMock()

    # Mock logs query
    log1 = MagicMock()
    log1.id = "log-1"
    log1.pipeline_id = "test-id"
    log1.log_content = "Log content 1"
    log1.timestamp = "2023-01-01T12:00:00"
    log1.status = "success"

    mock_db_session.query.return_value.filter.return_value.all.return_value = [
        log1]

    response = client.get("/api/build-logs/test-id")
    assert response.status_code == 200


@patch('main.jenkins_service')
def test_trigger_rollback(mock_jenkins, mock_db_session):
    # Mock pipeline
    pipeline = MagicMock()
    pipeline.id = "test-id"
    pipeline.name = "test-pipeline"

    # Mock pipeline existence check
    mock_db_session.query.return_value.filter.return_value.first.return_value = pipeline

    # Mock rollback success
    mock_jenkins.trigger_rollback.return_value = True

    response = client.post("/api/trigger-rollback/test-id")
    assert response.status_code == 200
    assert response.json()["pipeline_name"] == "test-pipeline"

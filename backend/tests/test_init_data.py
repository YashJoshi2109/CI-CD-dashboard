from init_data import init_sample_data
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def test_init_sample_data():
    # Mock the database session
    with patch('init_data.get_db') as mock_get_db:
        # Create a mock session
        mock_session = MagicMock()
        mock_get_db.return_value.__next__.return_value = mock_session

        # Run the initialization function
        init_sample_data()

        # Assert that add was called 3 times (for our 3 sample pipelines)
        assert mock_session.add.call_count == 3
        # Assert that commit was called
        mock_session.commit.assert_called_once()

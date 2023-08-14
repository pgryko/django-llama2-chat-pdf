from unittest.mock import patch

import pytest


# Helper function to mock an exception from replicate.run
@pytest.fixture
def mock_replicate_run_exception(*args, **kwargs):
    def _mock_run_exception(*args, **kwargs):
        raise Exception("Some error")

    with patch("replicate.run", _mock_run_exception):
        yield  # This yields control to the test function, keeping the patch in effect


# Helper function to mock the replicate.run behavior
@pytest.fixture
def mock_replicate_run():
    def mock_run(*args, **kwargs):
        yield "item1"
        yield "item2"

    # Patch the replicate.run function to use our mock_run
    with patch("replicate.run", mock_run):
        yield  # This yields control to the test function, keeping the patch in effect

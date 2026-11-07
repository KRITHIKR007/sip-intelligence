"""
SIP Intelligence — Pytest Configuration and Test Fixtures
"""
import pytest
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Ensure workspace root is on sys.path for ml imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

@pytest.fixture
def mock_text_document():
    return (
        "SECTION 1: SIGNALLING PLAN OVERVIEW\n"
        "Signal 101B controls route into Up Loop line. "
        "Distant signal 101D located at chainage 1200m.\n\n"
        "SECTION 2: TRACK CIRCUITS\n"
        "Track circuit TC 23 monitors crossover points 102A/B. "
        "Compliant with IRS-S 36 specification.\n\n"
        "SECTION 3: LEVEL CROSSING GATES\n"
        "Interlocked LC gate 42 provided with motor operation."
    )


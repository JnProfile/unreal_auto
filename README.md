# Pixel Streaming UI Automation Tests

This project contains automated tests for the Pixel Streaming web UI using Python, pytest, and Selenium.

## Prerequisites

- Python 3.12
- Chrome browser installed
- Pixel Streaming server running on http://127.0.0.1

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

To run all tests:
```bash
pytest
```

To run with detailed output:
```bash
pytest -v
```

To run with HTML report:
```bash
pytest --html=report.html
```

## Project Structure

- `conftest.py` - Contains pytest fixtures and configuration
- `pages/` - Contains page object classes
- `tests/` - Contains test files
- `baselines/` - Contains baseline screenshots for visual comparison

## Test Scenarios

The main test scenario covers:
1. Page load and button availability check
2. Play button functionality
3. Fullscreen toggle
4. Settings panel
5. Stats panel
6. Disconnection test
7. Reconnection attempt test

## Notes

- The first time you run the tests, baseline screenshots will be created automatically
- Make sure the Pixel Streaming server is running before executing tests
- Some tests include small delays to account for UI state changes 
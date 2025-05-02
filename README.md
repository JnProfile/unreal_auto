# Pixel Streaming UI Automation Tests

This project contains automated tests for the Pixel Streaming web UI using Python, pytest, and Selenium.

## Prerequisites

- Windows 10/11 machine
- Python 3.13
- Chrome browser installed

## Setup

1. Clone repository:
   ```bash
   git clone https://github.com/JnProfile/unreal_auto.git
   ```

2. Download and unzip UE5 project:
   - Place it in the root of unreal_auto directory
   - Ensure the relative path of VehicleTouch50_Launch.lnk is: `unreal_auto/VehicleTouch50/VehicleTouch50_Launch.lnk`

3. Start Pixel Streaming servers:
   ```bash
   # Run VehicleTouch50/PixelStreaming/WebServers/get_ps_servers.bat
   # Run VehicleTouch50/PixelStreaming\WebServers\SignallingWebServer\platform_scripts\cmd\setup.bat
   ```

4. Start the Signalling Server:
   ```bash
   # Run Start_WithTURN_SignallingServer.ps1 for the first time
   ```

5. Launch and test the application:
   - Run VehicleTouch50_Launch
   - Test the connection at http://127.0.0.1
   - Close app and signaling server

6. Set up Python environment:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On Unix/MacOS:
   source venv/bin/activate
   ```

7. Install dependencies:
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

- The first time you run the tests, baseline screenshots will be created automatically, next tests run will be with comparison of screenshots and baselines
- Make sure the Pixel Streaming server is running before executing tests
- Some tests include small delays to account for UI state changes 
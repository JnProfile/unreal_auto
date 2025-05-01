import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import subprocess
import psutil
import time
import json
from datetime import datetime

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "nondestructive: mark test as nondestructive"
    )
    config.option.selenium_exclude_debug = True

def pytest_runtest_makereport(item, call):
    if call.when == "call" and call.excinfo is not None:
        # Create failures directory if it doesn't exist
        failures_dir = "test_failures"
        if not os.path.exists(failures_dir):
            os.makedirs(failures_dir)
        
        # Get test information
        test_name = item.name
        test_class = item.cls.__name__ if item.cls else "NoClass"
        error_msg = str(call.excinfo.value)
        error_type = call.excinfo.type.__name__
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create failure log entry
        failure_data = {
            "test_name": f"{test_class}.{test_name}",
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_msg,
            "traceback": str(call.excinfo.traceback)
        }
        
        # Save to JSON file
        filename = f"{test_class}_{test_name}_{timestamp}.json"
        filepath = os.path.join(failures_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(failure_data, f, indent=2, ensure_ascii=False)

@pytest.fixture(scope="session")
def base_url():
    return "http://127.0.0.1:80"

@pytest.fixture(scope="session")
def signalling_server():
    """Fixture to start and manage the signalling server process"""
    # Get the absolute path to the script
    script_path = os.path.abspath("VehicleTouch50/PixelStreaming/WebServers/SignallingWebServer/platform_scripts/cmd/Start_WithTURN_SignallingServer.ps1")
    
    # Start the process
    process = subprocess.Popen(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    
    # Wait for the server to start
    time.sleep(5)
    
    yield process
    
    # Cleanup: terminate the process and all its children
    try:
        parent = psutil.Process(process.pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()

        
        # Wait for processes to terminate
        gone, alive = psutil.wait_procs([parent] + children, timeout=5)
        for p in alive:
            p.kill()  # Force kill if still alive
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

@pytest.fixture(scope="session")
def vehicle_touch_process():
    """Fixture to start and manage the VehicleTouch process"""
    shortcut_path = os.path.abspath("VehicleTouch50/VehicleTouch50_Launch.lnk")
    
    # Start the process
    process = subprocess.Popen(
        ["cmd", "/c", "start", "", shortcut_path],
        shell=True
    )
    
    # Wait for the application to start
    time.sleep(10)
    
    yield process
    
    # Try to terminate the process gracefully first
    try:
        process.terminate()
        process.wait(timeout=5)
    except (subprocess.TimeoutExpired, ProcessLookupError):
        # If graceful termination fails, force kill all VehicleTouch processes
        for proc in psutil.process_iter(['name']):
            try:
                if 'VehicleTouch50' in proc.info['name']:
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

@pytest.fixture(scope="session")
def driver(signalling_server, vehicle_touch_process):
    """Fixture to create and manage the WebDriver instance"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    yield driver
    
    driver.quit()

@pytest.fixture(scope="function")
def check_vehicle_touch_closed():
    """Fixture to check if VehicleTouch process is closed"""
    def _check():
        for proc in psutil.process_iter(['name']):
            try:
                if 'VehicleTouch50' in proc.info['name']:
                    return False
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return True
    
    return _check

@pytest.fixture(scope="session")
def baselines_dir():
    dir_path = os.path.join(os.path.dirname(__file__), "baselines")
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path 

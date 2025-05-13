"""
Launch script that starts the API server and runs the OpenAI integration test.
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Start the API server and run the OpenAI test."""
    # Get project root
    project_root = Path(__file__).resolve().parent
    
    # Set environment variables from .env
    env_path = project_root / ".env"
    if env_path.exists():
        logger.info(f"Loading environment variables from {env_path}")
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key] = value
                    if key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "API_SECRET_KEY"]:
                        logger.info(f"Set {key}={value[:5]}...")
    
    # Start the API server
    logger.info("Starting the API server...")
    server_process = subprocess.Popen(
        [sys.executable, str(project_root / "run_src_server.py")],
        cwd=str(project_root),
        env=os.environ.copy(),
    )
    
    # Wait for server to start
    logger.info("Waiting for server to start (10 seconds)...")
    time.sleep(10)
    
    try:
        # Run the OpenAI integration test
        logger.info("Running OpenAI integration test...")
        test_process = subprocess.run(
            [sys.executable, str(project_root / "test_openai_integration.py")],
            cwd=str(project_root),
            env=os.environ.copy(),
            check=True,
        )
        
        if test_process.returncode == 0:
            logger.info("OpenAI integration test completed successfully!")
        else:
            logger.error(f"OpenAI integration test failed with exit code {test_process.returncode}")
    
    finally:
        # Terminate the server process
        logger.info("Stopping the API server...")
        server_process.terminate()
        server_process.wait(timeout=10)
        logger.info("API server stopped.")

if __name__ == "__main__":
    main()

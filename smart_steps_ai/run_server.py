# Simple API server starter
import uvicorn
from smart_steps_ai.api import get_app

if __name__ == "__main__":
    print("Starting Smart Steps AI API Server...")
    app = get_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)

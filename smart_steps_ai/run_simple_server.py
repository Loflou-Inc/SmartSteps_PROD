# Simple minimal API server
from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="Smart Steps AI API",
    description="API for the Smart Steps AI Professional Persona module",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/v1/personas")
async def get_personas():
    # Return a simple mock response
    return {
        "personas": [
            {
                "id": "dr-morgan-hayes",
                "name": "Dr. Morgan Hayes",
                "specialization": "Cognitive Behavioral Therapy",
                "description": "CBT Therapist specializing in anxiety and depression"
            },
            {
                "id": "dr-alex-rivera",
                "name": "Dr. Alex Rivera",
                "specialization": "Behavioral Analysis",
                "description": "Behavioral Analyst focusing on pattern recognition and intervention"
            }
        ]
    }

@app.get("/api/v1/sessions")
async def get_sessions():
    # Return a simple mock response
    return {
        "sessions": [
            {
                "id": "session-001",
                "client_name": "John Doe",
                "persona_id": "dr-morgan-hayes",
                "created_at": "2025-05-11T09:00:00Z",
                "status": "active"
            }
        ]
    }

if __name__ == "__main__":
    print("Starting Simplified Smart Steps AI API Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)

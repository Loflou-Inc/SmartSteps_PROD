"""
API documentation utilities.

This module enhances the OpenAPI schema with detailed documentation, examples,
and authentication information.
"""

from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

def custom_openapi(app: FastAPI):
    """
    Create a custom OpenAPI schema with enhanced documentation.
    
    Args:
        app (FastAPI): The FastAPI application
        
    Returns:
        dict: The OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Smart Steps AI API",
        version="0.1.0",
        description="""
        # Smart Steps AI Professional Persona API
        
        This API provides access to the Smart Steps AI Professional Persona system, a tool for facilitators, 
        therapists, probation officers, and similar professionals.
        
        ## Key Features
        
        - **Professional Personas**: Create and manage AI-powered professional personas with detailed 
          backstories, expertise areas, and conversation styles.
        
        - **Sessions**: Manage therapeutic conversations between clients and professional personas.
        
        - **Advanced Memory System**: Access to multi-layered memory architecture (foundation, experience, 
          synthesis, meta-cognitive) for realistic and coherent conversation.
        
        - **Analysis**: Generate insights and reports from conversation sessions.
        
        ## Authentication
        
        This API uses JWT Bearer token authentication. To authenticate:
        
        1. Make a POST request to `/api/v1/auth/token` with your username and password
        2. Use the returned token in the Authorization header for subsequent requests:
           `Authorization: Bearer your_token_here`
        
        ## Rate Limiting
        
        The API implements rate limiting to prevent abuse. Exceeding the rate limit will result in
        429 Too Many Requests responses.
        
        ## Response Codes
        
        - 200: Success
        - 201: Created
        - 204: No Content (successful deletion)
        - 400: Bad Request (invalid input)
        - 401: Unauthorized (missing or invalid token)
        - 403: Forbidden (insufficient permissions)
        - 404: Not Found
        - 429: Too Many Requests (rate limit exceeded)
        - 500: Internal Server Error
        
        ## Support
        
        For support or questions, contact support@smartsteps.ai
        """,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"] = {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter JWT token"
            }
        }
    }
    
    # Apply security to all operations
    if "security" not in openapi_schema:
        openapi_schema["security"] = []
    
    openapi_schema["security"].append({"Bearer": []})
    
    # Add custom examples to paths
    
    # Session creation example
    if "/api/v1/sessions/" in openapi_schema["paths"]:
        path = openapi_schema["paths"]["/api/v1/sessions/"]
        if "post" in path:
            path["post"]["requestBody"]["content"]["application/json"]["examples"] = {
                "Initial Session": {
                    "summary": "Initial therapy session",
                    "value": {
                        "title": "Initial Assessment",
                        "client_id": "client-001",
                        "persona_id": "jane",
                        "provider_id": "openai",
                        "metadata": {
                            "purpose": "Initial assessment",
                            "referral_source": "Self-referred",
                            "priority": "Medium"
                        }
                    }
                },
                "Follow-up Session": {
                    "summary": "Follow-up therapy session",
                    "value": {
                        "title": "Weekly Check-in",
                        "client_id": "client-001",
                        "persona_id": "jane",
                        "provider_id": "anthropic",
                        "metadata": {
                            "purpose": "Follow-up",
                            "previous_session_id": "session-001",
                            "focus_areas": ["anxiety", "stress-management"]
                        }
                    }
                }
            }
    
    # Persona creation example
    if "/api/v1/personas/" in openapi_schema["paths"]:
        path = openapi_schema["paths"]["/api/v1/personas/"]
        if "post" in path:
            path["post"]["requestBody"]["content"]["application/json"]["examples"] = {
                "Therapist Persona": {
                    "summary": "Therapist persona example",
                    "value": {
                        "name": "jane-therapist",
                        "display_name": "Dr. Jane Thompson",
                        "version": "1.0.0",
                        "description": "Experienced therapist with a warm, empathetic approach",
                        "system_prompt": "You are Dr. Jane Thompson, a licensed clinical psychologist with 15 years of experience...",
                        "personality_traits": {
                            "empathy": 9,
                            "analytical": 7,
                            "patience": 8,
                            "directness": 6,
                            "formality": 6,
                            "warmth": 8,
                            "curiosity": 7,
                            "confidence": 8
                        },
                        "expertise_areas": ["anxiety disorders", "trauma recovery", "CBT", "mindfulness"],
                        "conversation_style": {
                            "greeting_format": "Hello {{client_name}}. How are you feeling today?",
                            "question_frequency": "medium",
                            "session_structure": ["check-in", "exploration", "intervention", "homework", "closing"],
                            "typical_phrases": [
                                "Let's explore that further",
                                "How did that make you feel?",
                                "That sounds challenging",
                                "I'm noticing a pattern here"
                            ]
                        },
                        "rules": [
                            "Maintain professional boundaries",
                            "Practice active listening",
                            "Validate client emotions",
                            "Focus on client strengths"
                        ]
                    }
                }
            }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

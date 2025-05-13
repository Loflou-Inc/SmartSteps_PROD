# Smart Steps AI Professional Persona Module - Technical Reference

## Introduction

This technical reference provides comprehensive documentation for developers, system integrators, and technical administrators working with the Smart Steps AI Professional Persona module. It covers API specifications, data models, integration patterns, and advanced configuration options.

## Table of Contents

1. [API Documentation](#api-documentation)
2. [Data Models](#data-models)
3. [Integration Patterns](#integration-patterns)
4. [Extending the System](#extending-the-system)
5. [Custom Persona Development](#custom-persona-development)
6. [Analytics Integration](#analytics-integration)
7. [Advanced Configuration](#advanced-configuration)
8. [Development Environment](#development-environment)
9. [Performance Considerations](#performance-considerations)
10. [API Security](#api-security)

## API Documentation

### API Overview

The Smart Steps API is a RESTful API that uses JSON for data exchange. The base URL is:

```
https://[your-server-domain]/api/v1
```

All API endpoints use HTTPS and require authentication using either JWT tokens or API keys.

### Authentication

#### API Key Authentication

```
Authorization: Bearer sk_ss_YOUR_API_KEY
```

#### JWT Authentication

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

To obtain a JWT token:

```http
POST /auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password"
}
```

Response:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-05-11T18:30:00Z"
}
```

### Session Endpoints

#### Create Session

```http
POST /sessions
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "client_id": "c12345",
  "persona_id": "dr_morgan_hayes",
  "goals": ["Explore coping strategies", "Discuss recent progress"],
  "duration_minutes": 45,
  "scheduled_at": "2025-05-15T14:00:00Z",
  "metadata": {
    "session_number": 5,
    "location": "virtual"
  }
}
```

Response:

```json
{
  "session_id": "s67890",
  "client_id": "c12345",
  "persona_id": "dr_morgan_hayes",
  "status": "scheduled",
  "scheduled_at": "2025-05-15T14:00:00Z",
  "duration_minutes": 45,
  "created_at": "2025-05-11T10:30:00Z",
  "created_by": "user@example.com",
  "goals": ["Explore coping strategies", "Discuss recent progress"],
  "metadata": {
    "session_number": 5,
    "location": "virtual"
  }
}
```

#### List Sessions

```http
GET /sessions?client_id=c12345&status=active,completed&limit=10&page=1
Authorization: Bearer YOUR_TOKEN
```

Response:

```json
{
  "sessions": [
    {
      "session_id": "s67890",
      "client_id": "c12345",
      "persona_id": "dr_morgan_hayes",
      "status": "completed",
      "started_at": "2025-05-10T14:00:00Z",
      "ended_at": "2025-05-10T14:45:00Z",
      "duration_minutes": 45
    },
    {
      "session_id": "s67891",
      "client_id": "c12345",
      "persona_id": "dr_alex_rivera",
      "status": "scheduled",
      "scheduled_at": "2025-05-15T14:00:00Z",
      "duration_minutes": 45
    }
  ],
  "pagination": {
    "total": 12,
    "page": 1,
    "page_size": 10,
    "pages": 2
  }
}
```

#### Get Session Details

```http
GET /sessions/s67890
Authorization: Bearer YOUR_TOKEN
```

Response:

```json
{
  "session_id": "s67890",
  "client_id": "c12345",
  "persona_id": "dr_morgan_hayes",
  "status": "completed",
  "scheduled_at": "2025-05-10T14:00:00Z",
  "started_at": "2025-05-10T14:00:00Z",
  "ended_at": "2025-05-10T14:45:00Z",
  "duration_minutes": 45,
  "goals": ["Explore coping strategies", "Discuss recent progress"],
  "summary": "Client discussed recent stressors at work and home...",
  "insights": [
    {
      "type": "pattern",
      "text": "Client frequently mentions feeling overwhelmed before social events",
      "confidence": 0.85
    },
    {
      "type": "progress",
      "text": "Client has shown improvement in using breathing techniques",
      "confidence": 0.92
    }
  ],
  "messages": [
    {
      "id": "m123456",
      "sender_type": "persona",
      "sender_id": "dr_morgan_hayes",
      "content": "Hello, how are you feeling today?",
      "timestamp": "2025-05-10T14:00:10Z"
    },
    {
      "id": "m123457",
      "sender_type": "client",
      "sender_id": "c12345",
      "content": "I've been feeling a bit stressed about work.",
      "timestamp": "2025-05-10T14:00:30Z"
    }
    // Additional messages...
  ],
  "facilitator_notes": [
    {
      "id": "n789012",
      "content": "Client appeared more relaxed than last session.",
      "timestamp": "2025-05-10T14:15:00Z",
      "author": "user@example.com"
    }
  ],
  "metadata": {
    "session_number": 5,
    "location": "virtual"
  }
}
```

#### Start Session

```http
POST /sessions/s67890/start
Authorization: Bearer YOUR_TOKEN
```

Response:

```json
{
  "session_id": "s67890",
  "status": "active",
  "started_at": "2025-05-11T10:35:00Z"
}
```

#### Send Message

```http
POST /sessions/s67890/messages
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "content": "Hello, how are you feeling today?",
  "sender_type": "persona"
}
```

Response:

```json
{
  "id": "m123456",
  "session_id": "s67890",
  "sender_type": "persona",
  "sender_id": "dr_morgan_hayes",
  "content": "Hello, how are you feeling today?",
  "timestamp": "2025-05-11T10:35:10Z"
}
```

#### End Session

```http
POST /sessions/s67890/end
Authorization: Bearer YOUR_TOKEN
```

Response:

```json
{
  "session_id": "s67890",
  "status": "completed",
  "started_at": "2025-05-11T10:35:00Z",
  "ended_at": "2025-05-11T11:20:00Z",
  "duration_minutes": 45
}
```

### Client Endpoints

#### Create Client

```http
POST /clients
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doe@example.com",
  "phone": "+1-234-567-8901",
  "date_of_birth": "1990-05-15",
  "metadata": {
    "referral_source": "Dr. Smith",
    "primary_concern": "Anxiety"
  }
}
```

Response:

```json
{
  "client_id": "c12345",
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doe@example.com",
  "phone": "+1-234-567-8901",
  "date_of_birth": "1990-05-15",
  "created_at": "2025-05-11T10:40:00Z",
  "created_by": "user@example.com",
  "metadata": {
    "referral_source": "Dr. Smith",
    "primary_concern": "Anxiety"
  }
}
```

#### List Clients

```http
GET /clients?search=Jane&limit=10&page=1
Authorization: Bearer YOUR_TOKEN
```

Response:

```json
{
  "clients": [
    {
      "client_id": "c12345",
      "first_name": "Jane",
      "last_name": "Doe",
      "email": "jane.doe@example.com",
      "created_at": "2025-05-11T10:40:00Z"
    }
  ],
  "pagination": {
    "total": 1,
    "page": 1,
    "page_size": 10,
    "pages": 1
  }
}
```

#### Get Client Details

```http
GET /clients/c12345
Authorization: Bearer YOUR_TOKEN
```

Response:

```json
{
  "client_id": "c12345",
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doe@example.com",
  "phone": "+1-234-567-8901",
  "date_of_birth": "1990-05-15",
  "created_at": "2025-05-11T10:40:00Z",
  "created_by": "user@example.com",
  "updated_at": "2025-05-11T10:40:00Z",
  "metadata": {
    "referral_source": "Dr. Smith",
    "primary_concern": "Anxiety"
  },
  "session_count": {
    "total": 5,
    "completed": 4,
    "scheduled": 1
  }
}
```

### Persona Endpoints

#### List Personas

```http
GET /personas
Authorization: Bearer YOUR_TOKEN
```

Response:

```json
{
  "personas": [
    {
      "persona_id": "dr_morgan_hayes",
      "name": "Dr. Morgan Hayes",
      "type": "therapist",
      "specialization": "cognitive_behavioral",
      "description": "Cognitive Behavioral Therapist specializing in anxiety and depression"
    },
    {
      "persona_id": "dr_alex_rivera",
      "name": "Dr. Alex Rivera",
      "type": "analyst",
      "specialization": "behavioral",
      "description": "Behavioral Analyst focusing on observable behaviors and reinforcement patterns"
    }
  ]
}
```

#### Get Persona Details

```http
GET /personas/dr_morgan_hayes
Authorization: Bearer YOUR_TOKEN
```

Response:

```json
{
  "persona_id": "dr_morgan_hayes",
  "name": "Dr. Morgan Hayes",
  "type": "therapist",
  "specialization": "cognitive_behavioral",
  "description": "Cognitive Behavioral Therapist specializing in anxiety and depression",
  "background": "Dr. Hayes has a background in clinical psychology with specialization in cognitive behavioral techniques...",
  "approach": "Dr. Hayes uses a collaborative, structured approach focusing on identifying and challenging negative thought patterns...",
  "techniques": ["cognitive restructuring", "behavioral activation", "mindfulness", "graded exposure"],
  "suitable_for": ["anxiety", "depression", "stress management", "phobias"],
  "avatar_url": "https://example.com/avatars/dr_morgan_hayes.png",
  "voice_settings": {
    "pitch": "medium",
    "rate": "medium",
    "style": "professional"
  },
  "communication_style": {
    "formality": 0.7,
    "directiveness": 0.6,
    "warmth": 0.8,
    "complexity": 0.5
  }
}
```

### Analysis Endpoints

#### Generate Session Summary

```http
POST /sessions/s67890/analyze/summary
Authorization: Bearer YOUR_TOKEN
```

Response:

```json
{
  "session_id": "s67890",
  "summary": "In this session, the client discussed ongoing work stress and recent social anxiety...",
  "key_points": [
    "Client reported increased work stress due to upcoming project deadline",
    "Social anxiety appears to be triggered primarily in group settings",
    "Client has been practicing breathing techniques with mixed results"
  ],
  "mood_analysis": {
    "primary": "anxious",
    "secondary": "frustrated",
    "confidence": 0.85
  },
  "recommended_focus_areas": [
    "Stress management techniques",
    "Gradual exposure to social situations",
    "Self-care planning"
  ]
}
```

#### Generate Progress Report

```http
POST /clients/c12345/analyze/progress
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "start_date": "2025-04-01",
  "end_date": "2025-05-11",
  "focus_areas": ["anxiety", "coping_strategies"]
}
```

Response:

```json
{
  "client_id": "c12345",
  "report_period": {
    "start": "2025-04-01",
    "end": "2025-05-11"
  },
  "sessions_analyzed": 5,
  "progress_summary": "Jane has shown steady improvement in anxiety management over the past 6 weeks...",
  "metrics": {
    "anxiety_level": {
      "trend": "decreasing",
      "start_value": 8,
      "current_value": 5,
      "change_percentage": -37.5
    },
    "coping_strategy_usage": {
      "trend": "increasing",
      "start_value": 2,
      "current_value": 6,
      "change_percentage": 200
    }
  },
  "patterns": [
    {
      "description": "Client reports better anxiety management in work settings, but continues to struggle in social gatherings",
      "confidence": 0.92
    }
  ],
  "recommendations": [
    "Continue practicing mindfulness techniques",
    "Gradual exposure to social situations with specific coping strategies",
    "Consider session focus on anticipatory anxiety before social events"
  ]
}
```

## Data Models

### Session Model

| Field | Type | Description |
|-------|------|-------------|
| session_id | string | Unique identifier for the session |
| client_id | string | Identifier for the client |
| persona_id | string | Identifier for the AI persona |
| status | string | Session status (scheduled, active, completed, cancelled) |
| scheduled_at | datetime | Scheduled start time |
| started_at | datetime | Actual start time |
| ended_at | datetime | End time |
| duration_minutes | integer | Planned session duration |
| goals | array | Array of session goals |
| summary | string | Session summary (generated after completion) |
| insights | array | Array of insight objects |
| messages | array | Array of message objects |
| facilitator_notes | array | Array of note objects |
| metadata | object | Flexible key-value metadata |

### Client Model

| Field | Type | Description |
|-------|------|-------------|
| client_id | string | Unique identifier for the client |
| first_name | string | Client's first name |
| last_name | string | Client's last name |
| email | string | Email address |
| phone | string | Phone number |
| date_of_birth | date | Birth date |
| created_at | datetime | Account creation timestamp |
| created_by | string | Creator's user ID |
| updated_at | datetime | Last update timestamp |
| metadata | object | Flexible key-value metadata |

### Persona Model

| Field | Type | Description |
|-------|------|-------------|
| persona_id | string | Unique identifier for the persona |
| name | string | Display name |
| type | string | Persona type (therapist, analyst, counselor) |
| specialization | string | Area of specialization |
| description | string | Short description |
| background | string | Detailed background information |
| approach | string | Therapeutic approach description |
| techniques | array | Array of techniques/methods used |
| suitable_for | array | Appropriate use cases |
| avatar_url | string | URL to avatar image |
| voice_settings | object | Voice configuration |
| communication_style | object | Style parameters |

### Message Model

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique message identifier |
| session_id | string | Associated session |
| sender_type | string | Type of sender (persona, client, facilitator) |
| sender_id | string | Identifier of the sender |
| content | string | Message content |
| timestamp | datetime | Message timestamp |
| metadata | object | Additional message metadata |

## Integration Patterns

### REST API Integration

The primary integration method is through the REST API. Follow these best practices:

1. **Authentication**: Use JWT tokens for user-based actions or API keys for system integrations.
2. **Pagination**: All list endpoints support pagination with `page` and `limit` parameters.
3. **Rate Limiting**: Implement appropriate rate limiting and backoff strategies.
4. **Error Handling**: Process HTTP status codes and error messages properly.
5. **Webhooks**: Use webhooks for event-driven integrations.

### Webhook Integration

Smart Steps supports webhooks for real-time notifications of events:

#### Register Webhook

```http
POST /webhooks
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "url": "https://your-system.example.com/webhook",
  "events": ["session.started", "session.ended", "client.created"],
  "secret": "your_webhook_secret"
}
```

Response:

```json
{
  "webhook_id": "wh12345",
  "url": "https://your-system.example.com/webhook",
  "events": ["session.started", "session.ended", "client.created"],
  "created_at": "2025-05-11T12:00:00Z",
  "status": "active"
}
```

#### Webhook Payload Example

```json
{
  "event": "session.ended",
  "timestamp": "2025-05-11T13:45:00Z",
  "data": {
    "session_id": "s67890",
    "client_id": "c12345",
    "persona_id": "dr_morgan_hayes",
    "started_at": "2025-05-11T13:00:00Z",
    "ended_at": "2025-05-11T13:45:00Z"
  }
}
```

### Unity Integration

The Smart Steps Unity client uses the C# SDK for integration. Here's a basic usage example:

```csharp
// Initialize the client
SmartStepsClient client = new SmartStepsClient(
    endpoint: "https://your-server.example.com/api",
    apiKey: "your_api_key"
);

// Start a session
Session session = await client.StartSessionAsync(
    clientId: "c12345",
    personaId: "dr_morgan_hayes"
);

// Send a message
Message message = await client.SendMessageAsync(
    sessionId: session.SessionId,
    content: "Hello, how are you feeling today?",
    senderType: SenderType.Persona
);

// Get session history
List<Message> messages = await client.GetSessionMessagesAsync(
    sessionId: session.SessionId
);
```
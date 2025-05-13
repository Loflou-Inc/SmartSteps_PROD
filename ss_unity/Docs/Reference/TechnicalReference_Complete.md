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
```### API Documentation Generation

Smart Steps uses OpenAPI/Swagger for API documentation:

```bash
# Generate OpenAPI documentation
python -m smart_steps_ai.tools.gen_openapi --output docs/api/openapi.json

# Run Swagger UI for interactive documentation
python -m smart_steps_ai.tools.swagger_ui
```

## Performance Considerations

### Scaling Strategies

#### Vertical Scaling

Configure worker processes based on available CPU cores:

```yaml
server:
  workers: 8  # Set to number of CPU cores
  worker_connections: 1000
```

#### Horizontal Scaling

For high-traffic deployments, use horizontal scaling with a load balancer:

1. **Load Balancer Configuration**:
   - Use a round-robin or least connections algorithm
   - Enable sticky sessions for WebSocket connections
   - Configure health checks with `/api/health` endpoint

2. **Shared Storage**:
   - Configure a shared file system or object storage for session data
   - Use a centralized database like MongoDB

3. **Stateless Operation**:
   - Design API handlers to be stateless
   - Store session state in the database or cache

Example Nginx load balancer configuration:

```nginx
upstream smartsteps {
    least_conn;
    server server1.example.com:8543;
    server server2.example.com:8543;
    server server3.example.com:8543;
}

server {
    listen 80;
    server_name api.smartsteps.example.com;

    location / {
        proxy_pass http://smartsteps;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Caching Strategies

Smart Steps implements several caching layers:

1. **Memory Cache**:
   - In-memory LRU cache for frequently accessed data
   - Configurable size limit to prevent memory issues

2. **Disk Cache**:
   - Persistent cache for larger objects
   - Useful for session transcripts and analysis results

3. **Distributed Cache**:
   - Optional Redis cache for multi-server deployments
   - Supports cache invalidation across servers

Configuration example:

```yaml
performance:
  cache:
    enabled: true
    memory_cache_size_mb: 256
    disk_cache_enabled: true
    disk_cache_path: /var/lib/smartsteps/cache
    ttl_seconds: 3600
    redis:
      enabled: false  # Enable for multi-server deployments
      host: localhost
      port: 6379
      db: 0
```

### Database Optimization

#### File-based Storage

For file-based storage, optimize with:

```yaml
storage:
  type: file
  optimization:
    auto_vacuum: true
    index_optimization: true
    compact_on_startup: true
    max_files_per_directory: 1000
    shard_by_date: true
```

#### MongoDB Optimization

For MongoDB, configure connection pooling and indexing:

```yaml
storage:
  type: mongodb
  connection:
    host: mongodb.example.com
    port: 27017
    database: smartsteps
    auth_source: admin
    username: smartsteps
    password: your_password
    max_pool_size: 100
    min_pool_size: 10
    max_idle_time_ms: 10000
  optimization:
    create_indexes: true
    read_preference: secondaryPreferred
    write_concern:
      w: 1
      j: true
```

### Memory Management

To optimize memory usage:

```yaml
performance:
  memory:
    max_memory_percent: 80
    vector_compression: true
    batch_processing: true
    garbage_collection_interval: 300
    low_memory_mode: false  # Enable for low-resource environments
```

### Response Time Optimization

Techniques to minimize API response times:

1. **Asynchronous Processing**:
   - Use background tasks for intensive operations
   - Implement webhooks for completion notifications

2. **Query Optimization**:
   - Limit fields returned by API endpoints
   - Use pagination for large result sets
   - Implement efficient database queries

3. **Compression**:
   - Enable HTTP compression for API responses
   - Use efficient serialization formats

Configuration example:

```yaml
server:
  compression: true
  compression_level: 6
  min_compression_size: 1024
  async_tasks:
    enabled: true
    max_workers: 4
    queue_size: 100
```

## API Security

### Authentication Methods

Smart Steps supports multiple authentication methods:

1. **API Keys**:
   - Used for system-to-system integration
   - Long-lived, high-privilege access
   - Format: `sk_ss_` prefix followed by random string

2. **JWT Tokens**:
   - Used for user authentication
   - Short-lived with refresh capability
   - Contains user identity and role information

3. **OAuth 2.0** (optional):
   - Integration with external identity providers
   - Support for standard OAuth flows
   - Configurable scopes for fine-grained permissions

### API Key Management

Best practices for API key management:

1. **Rotation**: Rotate keys regularly (every 90 days recommended)
2. **Revocation**: Implement immediate key revocation capability
3. **Monitoring**: Track and alert on suspicious usage patterns
4. **Restriction**: Limit keys by IP address or usage pattern
5. **Scoping**: Create keys with minimal required permissions

API key configuration:

```yaml
security:
  api_keys:
    prefix: "sk_ss_"
    length: 32
    expiration:
      enabled: true
      days: 90
    rate_limiting:
      enabled: true
      rate: "1000/minute"
```

### Request Signing

For enhanced security, implement request signing:

```http
POST /api/v1/sessions
Host: api.smartsteps.example.com
Date: Sun, 11 May 2025 15:30:00 GMT
Authorization: Bearer sk_ss_YOUR_API_KEY
X-Signature-Timestamp: 1715438400
X-Signature: sha256=5d2eee3fa451756a34c1a3b6d95e52af56c602ccc98b5418cf747bd8c300dec1
Content-Type: application/json

{
  "client_id": "c12345",
  "persona_id": "dr_morgan_hayes"
}
```

The signature is generated using:

```python
import hashlib
import hmac
import time

def generate_signature(api_key_secret, body, timestamp):
    message = f"{timestamp}{body}"
    signature = hmac.new(
        api_key_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

# Usage
timestamp = int(time.time())
body = '{"client_id":"c12345","persona_id":"dr_morgan_hayes"}'
signature = generate_signature("your_api_key_secret", body, timestamp)
```

### Rate Limiting

Smart Steps implements tiered rate limiting:

1. **Global Limits**: Applied to all API requests
2. **Endpoint-Specific Limits**: Different limits for different endpoints
3. **User-Based Limits**: Limits based on user role or client
4. **IP-Based Limits**: Protection against distributed attacks

Configuration example:

```yaml
security:
  rate_limiting:
    enabled: true
    default_limit: "100/minute"
    per_endpoint:
      "/api/v1/auth/login": "20/minute"
      "/api/v1/auth/password/reset": "10/hour"
    per_user:
      default: "1000/hour"
      admin: "5000/hour"
    ip_whitelist: ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
```

### Data Protection

Smart Steps implements several data protection measures:

1. **Transport Security**: 
   - TLS 1.3 for all communications
   - Strong cipher suites
   - Certificate validation

2. **Field-Level Encryption**:
   - Sensitive client data encrypted at rest
   - Separate encryption keys for different data categories
   - Key rotation support

3. **Anonymization**:
   - Data anonymization for analytics and research
   - Configurable anonymization levels
   - Consent tracking for data usage

Configuration example:

```yaml
security:
  encryption:
    algorithm: "AES-256-GCM"
    key_management:
      key_rotation_days: 90
      minimum_key_versions: 3
    
    encrypted_fields:
      client:
        - "full_name"
        - "date_of_birth"
        - "address"
        - "contact_information"
      session:
        - "notes"
        - "assessment"
```

### Security Headers

Implement secure HTTP headers:

```yaml
security:
  headers:
    Content-Security-Policy: "default-src 'self'"
    X-Content-Type-Options: "nosniff"
    X-Frame-Options: "DENY"
    X-XSS-Protection: "1; mode=block"
    Strict-Transport-Security: "max-age=31536000; includeSubDomains"
    Referrer-Policy: "strict-origin-when-cross-origin"
```

## WebSocket API

In addition to the REST API, Smart Steps provides a WebSocket API for real-time communication.

### Connection Establishment

Connect to the WebSocket endpoint:

```
wss://api.smartsteps.example.com/ws
```

Include authentication in the connection request:

```javascript
const socket = new WebSocket('wss://api.smartsteps.example.com/ws', [], {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});
```

### Message Format

All WebSocket messages use a consistent JSON format:

```json
{
  "type": "message_type",
  "id": "unique_message_id",
  "data": {
    // Message-specific data
  }
}
```

### Event Types

The WebSocket API supports the following event types:

#### Client → Server

1. **join_session**:
   ```json
   {
     "type": "join_session",
     "id": "msg1",
     "data": {
       "session_id": "s67890"
     }
   }
   ```

2. **leave_session**:
   ```json
   {
     "type": "leave_session",
     "id": "msg2",
     "data": {
       "session_id": "s67890"
     }
   }
   ```

3. **send_message**:
   ```json
   {
     "type": "send_message",
     "id": "msg3",
     "data": {
       "session_id": "s67890",
       "content": "Hello, how are you feeling today?",
       "sender_type": "persona"
     }
   }
   ```

4. **typing_indicator**:
   ```json
   {
     "type": "typing_indicator",
     "id": "msg4",
     "data": {
       "session_id": "s67890",
       "sender_type": "client",
       "is_typing": true
     }
   }
   ```

#### Server → Client

1. **session_update**:
   ```json
   {
     "type": "session_update",
     "id": "srv1",
     "data": {
       "session_id": "s67890",
       "status": "active",
       "started_at": "2025-05-11T15:30:00Z"
     }
   }
   ```

2. **new_message**:
   ```json
   {
     "type": "new_message",
     "id": "srv2",
     "data": {
       "message": {
         "id": "m123456",
         "session_id": "s67890",
         "sender_type": "persona",
         "sender_id": "dr_morgan_hayes",
         "content": "Hello, how are you feeling today?",
         "timestamp": "2025-05-11T15:30:10Z"
       }
     }
   }
   ```

3. **typing_indicator**:
   ```json
   {
     "type": "typing_indicator",
     "id": "srv3",
     "data": {
       "session_id": "s67890",
       "sender_type": "persona",
       "sender_id": "dr_morgan_hayes",
       "is_typing": true
     }
   }
   ```

4. **error**:
   ```json
   {
     "type": "error",
     "id": "srv4",
     "data": {
       "code": "session_not_found",
       "message": "The specified session was not found",
       "request_id": "msg1"
     }
   }
   ```

### Error Handling

WebSocket errors follow a standard format:

| Error Code | Description | HTTP Equivalent |
|------------|-------------|----------------|
| authentication_error | Authentication failure | 401 |
| permission_denied | Insufficient permissions | 403 |
| session_not_found | Session not found | 404 |
| invalid_request | Invalid request format | 400 |
| rate_limited | Too many requests | 429 |
| internal_error | Server error | 500 |

### WebSocket Client Example

JavaScript client example:

```javascript
const token = 'YOUR_JWT_TOKEN';
const socket = new WebSocket('wss://api.smartsteps.example.com/ws');

socket.onopen = () => {
  console.log('Connection established');
  
  // Join a session
  socket.send(JSON.stringify({
    type: 'join_session',
    id: 'msg1',
    data: {
      session_id: 's67890'
    }
  }));
};

socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'session_update':
      console.log('Session updated:', message.data);
      break;
    
    case 'new_message':
      console.log('New message:', message.data.message);
      // Update UI with new message
      break;
    
    case 'typing_indicator':
      console.log('Typing indicator:', message.data);
      // Show/hide typing indicator
      break;
    
    case 'error':
      console.error('Error:', message.data);
      break;
  }
};

socket.onclose = (event) => {
  console.log('Connection closed:', event.code, event.reason);
};

// Send a message
function sendMessage(content) {
  socket.send(JSON.stringify({
    type: 'send_message',
    id: 'msg' + Date.now(),
    data: {
      session_id: 's67890',
      content: content,
      sender_type: 'client'
    }
  }));
}
```

## Command Line Tools

The Smart Steps module includes several command-line tools for administration and development.

### Server Management

```bash
# Start the server
python -m smart_steps_ai.server

# Start with specific configuration
python -m smart_steps_ai.server --config /path/to/config.yaml

# Start in development mode
python -m smart_steps_ai.server --debug
```

### Database Management

```bash
# Initialize the database
python -m smart_steps_ai.db.init --config /path/to/config.yaml

# Migrate the database
python -m smart_steps_ai.db.migrate --config /path/to/config.yaml

# Backup the database
python -m smart_steps_ai.db.backup --output /path/to/backup.zip

# Restore from backup
python -m smart_steps_ai.db.restore --input /path/to/backup.zip
```

### User Management

```bash
# Create a new user
python -m smart_steps_ai.cli user create --username admin --email admin@example.com --role admin

# List all users
python -m smart_steps_ai.cli user list

# Reset user password
python -m smart_steps_ai.cli user reset-password --username admin
```

### API Key Management

```bash
# Generate a new API key
python -m smart_steps_ai.cli apikey generate --name "Unity Client" --expiry 365

# List all API keys
python -m smart_steps_ai.cli apikey list

# Revoke an API key
python -m smart_steps_ai.cli apikey revoke --id sk_ss_abc123
```

### Testing and Development

```bash
# Run all tests
python -m smart_steps_ai.test

# Generate test data
python -m smart_steps_ai.tools.generate_test_data --clients 50 --sessions 200

# Start interactive persona test
python -m smart_steps_ai.tools.test_persona --persona dr_morgan_hayes
```

## Appendix

### Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request format or parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource conflict |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

### Error Response Format

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      "field": "specific_field",
      "reason": "specific reason"
    },
    "request_id": "unique_request_id"
  }
}
```

### Common Error Codes

| Error Code | Description |
|------------|-------------|
| authentication_error | Authentication failure |
| permission_denied | Insufficient permissions |
| resource_not_found | Resource not found |
| validation_error | Request validation failed |
| rate_limited | Rate limit exceeded |
| internal_error | Internal server error |

### SDK Documentation

For detailed SDK documentation, see:

- [Python SDK](../sdk/python/README.md)
- [JavaScript SDK](../sdk/javascript/README.md)
- [C# SDK](../sdk/csharp/README.md)

### API Versioning

The Smart Steps API uses semantic versioning:

- **Major version changes** (v1 → v2): Breaking changes, not backward compatible
- **Minor version changes** (v1.1 → v1.2): New features, backward compatible
- **Patch version changes** (v1.1.1 → v1.1.2): Bug fixes, backward compatible

API version is specified in the URL path: `/api/v1/resource`

### Deprecation Policy

1. APIs are supported for at least 12 months after deprecation notice
2. Deprecated endpoints return a warning header: `X-API-Warning: This endpoint is deprecated`
3. Migration guides are provided for all breaking changes
4. Sunset dates are communicated at least 6 months in advance

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-05-11 | Technical Team | Initial creation |

**Review Schedule**: This document should be reviewed and updated at least quarterly or when significant API changes occur.
# Unity Integration Guide

This guide explains how to integrate the Smart Steps AI system with a Unity application using the provided C# client library.

## Overview

The Smart Steps AI Unity integration provides a seamless way to incorporate AI professional personas, therapy session management, and conversation capabilities into your Unity application. The integration consists of:

1. **SmartStepsApiClient**: A low-level client for direct API communication
2. **SmartStepsAIManager**: A high-level manager that simplifies integration
3. **Model classes**: C# classes that mirror the API data structures
4. **Example components**: Ready-to-use examples demonstrating integration

## Getting Started

### 1. Import the Package

Copy the `SmartStepsAI` folder into your Unity project's `Assets/Scripts` directory. This folder contains all the necessary scripts for integration.

### 2. Configuration

The integration requires a running Smart Steps AI API server. By default, it will connect to `http://localhost:8000`, but you can configure this in the `SmartStepsAIManager`.

### 3. Basic Setup

Add the `SmartStepsAIManager` component to a GameObject in your scene, or access it via the singleton instance:

```csharp
// Get the manager instance
var aiManager = SmartStepsAIManager.Instance;

// Configure the API URL if needed
aiManager.SetApiUrl("http://your-api-server:8000");

// Log in to the API
aiManager.Login("username", "password");
```

### 4. Event Handling

Register for events to handle various AI interactions:

```csharp
// Register event handlers
aiManager.OnAuthenticationChanged += (isAuthenticated) => {
    Debug.Log($"Authentication changed: {isAuthenticated}");
};

aiManager.OnMessageReceived += (message) => {
    Debug.Log($"Received message: {message.content}");
};

aiManager.OnError += (error) => {
    Debug.LogError($"AI Error: {error}");
};
```

## Core Features

### Authentication

```csharp
// Log in with credentials
aiManager.Login("username", "password");

// Check authentication status
bool isAuthenticated = aiManager.IsAuthenticated();
```

### Persona Management

```csharp
// Load available personas
aiManager.LoadAvailablePersonas();

// Get a specific persona
aiManager.LoadPersona("persona_id");

// Access the current persona
var currentPersona = aiManager.CurrentPersona;
```

### Session Management

```csharp
// Create a new session
aiManager.CreateSession("Session Title", "persona_id");

// Load an existing session
aiManager.LoadSession("session_id");

// Access the current session
var currentSession = aiManager.CurrentSession;
```

### Conversation

```csharp
// Send a message
aiManager.SendMessage("Hello, how are you?");

// Get conversation history
aiManager.GetConversationHistory(50, (messages, error) => {
    if (messages != null) {
        foreach (var message in messages) {
            Debug.Log($"{message.sender_type}: {message.content}");
        }
    }
});
```

### Analysis

```csharp
// Analyze the current session
aiManager.AnalyzeCurrentSession("standard", (analysis, error) => {
    if (analysis != null) {
        Debug.Log($"Session Summary: {analysis.summary}");
    }
});

// Get client insights
aiManager.GetClientInsights("all", 10, (insights, error) => {
    if (insights != null) {
        foreach (var insight in insights) {
            Debug.Log($"Insight: {insight.content}");
        }
    }
});

// Generate a client report
aiManager.GenerateClientReport("html", "all", (report, error) => {
    if (report != null) {
        Debug.Log($"Report Content: {report.content}");
    }
});
```

## Example: Conversation UI

The package includes an example conversation UI component (`AIConversationExample`) that demonstrates a complete integration. To use it:

1. Create a new scene with UI elements (input field, buttons, message container)
2. Add the `AIConversationExample` component to a GameObject
3. Configure the serialized fields in the inspector
4. Create message prefabs for client and AI messages

For more details, see the example code and comments in `AIConversationExample.cs`.

## Advanced Usage

### Direct API Access

If you need more control, you can use the `SmartStepsApiClient` directly:

```csharp
// Create client
var apiClient = new SmartStepsApiClient("http://your-api-server:8000", this);

// Authenticate
apiClient.Authenticate("username", "password", (success, error) => {
    if (success) {
        // Make API calls
        apiClient.ListPersonas(null, null, 50, 0, (response, err) => {
            // Process response
        });
    }
});
```

### Custom Data Models

The model classes match the API data structures. You can extend or modify them as needed for your application.

## Troubleshooting

### Common Issues

1. **Connection Failures**: Ensure the API server is running and accessible from Unity
2. **Authentication Errors**: Verify your credentials and check if the token has expired
3. **Missing References**: Make sure all prefabs and UI elements are assigned in the inspector

### Debug Logging

The integration includes extensive debug logging. Check the Unity console for error messages and API interaction details.

## API Reference

For a complete reference of the API endpoints and data structures, see the [API Documentation](./index.md).

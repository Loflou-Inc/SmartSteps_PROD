# Scenario Engine: Design & Implementation Plan

**Last Updated:** May 14, 2025  
**Status:** Planned - Critical Priority

## Overview

The Scenario Engine is a core component of the SmartSteps platform, representing **Phase 1** of the patented three-phase process. This document outlines the design and implementation plan for creating a robust scenario system that aligns with patent claims while providing practical value to practitioners and clients.

## Patent Alignment

The Scenario Engine directly implements these aspects of the patent application:

> "The psychological assessment involves assessing a situation where the practitioner and client are active participants... The psychological process involves depicting situations where often undisclosed behavior or behaviors are brought to the fore using a character within the scenario as the scapegoat and point of discussion."

> "The scenario phase where choices are made by the participants..."

> "Users, including both practitioners and clients, will be guided through structured, interactive scenarios. Each scenario presents decision points and behavioral dilemmas intended to elicit discussion and self-reflection."

## Core Components

### 1. Scenario Data Model

```csharp
// Key data structures for the Scenario Engine
public class Scenario 
{
    public string Id { get; set; }
    public string Title { get; set; }
    public string Description { get; set; }
    public List<ScenarioStage> Stages { get; set; }
    public Dictionary<string, object> Metadata { get; set; }
    public List<string> Tags { get; set; }
    public ScenarioCategory Category { get; set; }
    public DifficultyLevel Difficulty { get; set; }
    public List<SELConstruct> TargetConstructs { get; set; }
}

public class ScenarioStage
{
    public string Id { get; set; }
    public string Content { get; set; }
    public string ImagePath { get; set; }
    public List<DecisionPoint> DecisionPoints { get; set; }
    public Dictionary<string, object> Metadata { get; set; }
    public StageType Type { get; set; }
}

public class DecisionPoint
{
    public string Id { get; set; }
    public string Prompt { get; set; }
    public List<Choice> Choices { get; set; }
    public bool IsRequired { get; set; }
    public Dictionary<string, object> Metadata { get; set; }
}

public class Choice
{
    public string Id { get; set; }
    public string Text { get; set; }
    public Dictionary<string, float> SELScores { get; set; }
    public Dictionary<string, object> Outcomes { get; set; }
    public string NextStageId { get; set; }
}

// Enums for categorization
public enum ScenarioCategory 
{
    Workplace,
    Relationship,
    Family,
    Education,
    SelfCare,
    Conflict,
    Ethical,
    Social
}

public enum SELConstruct
{
    SelfAwareness,
    SelfManagement,
    SocialAwareness,
    RelationshipSkills,
    ResponsibleDecisionMaking,
    SelfDisclosure
}

public enum StageType
{
    Introduction,
    MainScenario,
    Decision,
    Consequence,
    Reflection,
    Conclusion
}

public enum DifficultyLevel
{
    Beginner,
    Intermediate,
    Advanced,
    Expert
}
```

### 2. Scenario Management System

#### Core Functionality:
- Scenario loading and initialization
- Stage progression management
- Decision point processing
- Choice outcome mapping
- Session state tracking
- Data collection for analysis

#### API Interface:
```csharp
public interface IScenarioManager
{
    // Core scenario functions
    Task<Scenario> LoadScenarioAsync(string scenarioId);
    Task<ScenarioInstance> StartScenarioAsync(string scenarioId, string sessionId);
    Task<ScenarioStage> GetCurrentStageAsync(string instanceId);
    Task<ScenarioStage> ProcessChoiceAsync(string instanceId, string decisionPointId, string choiceId);
    Task<bool> CompleteScenarioAsync(string instanceId);
    
    // Management functions
    Task<List<Scenario>> ListScenariosAsync(ScenarioFilter filter = null);
    Task<bool> SaveScenarioAsync(Scenario scenario);
    Task<bool> DeleteScenarioAsync(string scenarioId);
    
    // Analysis helpers
    Task<ScenarioResults> GetScenarioResultsAsync(string instanceId);
    Task<List<Choice>> GetUserChoicesAsync(string instanceId);
}
```

### 3. Scenario Authoring Tools

#### Features:
- Scenario template system
- Stage and decision point editor
- Branching path visualization
- SEL construct tagging
- Metadata management
- Image/media integration

#### Implementation Approach:
- Create Unity editor extension for scenario authoring
- Implement JSON import/export for scenarios
- Develop web-based scenario editor for non-technical users
- Support collaborative editing with version control

### 4. Scenario Runtime System

#### Features:
- Dynamic content loading
- State management across stages
- Choice recording and tracking
- Integration with AI Persona for commentary
- Event system for UI updates
- Session progress tracking

#### Implementation Approach:
- Create ScenarioManager singleton in Unity
- Implement IScenarioService in backend API
- Develop state persistence layer
- Build event system for UI notifications
- Create adapters for different presentation modes

### 5. User Interface Components

#### Practitioner Interface:
- Scenario browser and selection tools
- Session configuration options
- Real-time progress monitoring
- Intervention tools and guidance
- Notes and observation recording

#### Client Interface:
- Engaging scenario presentation
- Clear decision point UI
- Choice selection with feedback
- Progress indication
- Reflection prompts

## Initial Scenario Library

The minimal viable implementation will include these core scenarios:

1. **"The Meeting"** - Workplace scenario focused on social awareness and relationship skills
2. **"The Wallet"** - Ethical dilemma emphasizing responsible decision making
3. **"The Argument"** - Interpersonal conflict highlighting self-management and social awareness
4. **"The Critique"** - Performance feedback scenario for self-awareness
5. **"The Request"** - Boundary-setting scenario for relationship skills

Each scenario will include:
- 4-6 stages with branching paths
- 2-3 key decision points
- 3-5 choices per decision point
- SEL construct scoring for each choice
- Tagged metadata for analysis

## Implementation Phases

### Phase 1: Core Framework (1-2 weeks)
- Implement data models and interfaces
- Create basic scenario loading and progression
- Develop simple UI for scenario presentation
- Implement choice recording
- Create test scenario in JSON format

### Phase 2: Basic Scenario Flow (2-3 weeks)
- Implement branching logic based on choices
- Create basic authoring tools
- Develop initial scenario library (5 scenarios)
- Integrate with session management
- Implement basic reporting

### Phase 3: Integration (3-4 weeks)
- Connect with AI Persona for commentary
- Implement handoff to Query Phase
- Add metadata collection for Analysis Phase
- Develop practitioner monitoring tools
- Create comprehensive logging for analysis

### Phase 4: Enhancement (4-6 weeks)
- Refine UI/UX for engagement
- Expand scenario library
- Implement advanced authoring tools
- Add media enhancements (images, audio)
- Develop scenario recommendation system

## Technology Stack

- **Frontend**: Unity UI system, C# models
- **Backend**: FastAPI endpoints, Python models
- **Storage**: JSON for scenario definitions, relational DB for instance data
- **Integration**: REST APIs and WebSockets for real-time updates

## Quality Assurance

- **Unit Tests**: Test scenario progression logic, branching paths
- **Integration Tests**: Verify scenario completion triggers query phase
- **User Testing**: Validate scenario clarity and engagement
- **Performance Testing**: Ensure smooth loading and transitions

## Unity-Specific Implementation

### UI Components
- ScenarioView prefab for presenting scenario content
- DecisionPointPanel for displaying choices
- StageTransition effects for smooth flow
- FacilitatorOverlay for practitioner guidance
- ProgressIndicator for session tracking

### Architecture
- ScenarioManager singleton coordinates overall flow
- ScenarioRenderer manages visual presentation
- ChoiceProcessor handles decision logic
- ScenarioDataService handles backend communication
- ScenarioEventSystem coordinates UI updates

### Integration Points
- SmartStepsAIManager for AI persona commentary
- SessionManager for tracking overall session state
- AnalyticsManager for recording metrics
- UserManager for role-based access

## Conclusion

The Scenario Engine is a critical component for aligning the SmartSteps platform with its patent claims. This document provides a comprehensive plan for implementing a robust, flexible scenario system that supports the psychological assessment process described in the patent while delivering practical value to practitioners and clients.

By implementing the Scenario Engine as outlined above, we will close a significant gap in the current implementation and establish the foundation for the complete three-phase process.

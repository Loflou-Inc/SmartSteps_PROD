# Scene Structure for Smart Steps

This document outlines the standard scene structure for the Smart Steps application.

## Main Menu Scene

```
- Canvas (Main Menu UI)
  - Header Panel
    - Logo
    - Version Text
  - Login Panel
    - Username Input
    - Password Input
    - Login Button
    - Remember Me Toggle
  - Navigation Panel
    - Client Management Button
    - Sessions Button
    - Reports Button
    - Settings Button
  - Footer Panel
    - Copyright Text
    - Support Button

- Systems
  - SmartStepsManager
  - UIManager
  - AudioManager
  - DataManager
```

## Client Session Scene

```
- Canvas (Session UI)
  - Header Panel
    - Client Info
    - Session Timer
    - Navigation Controls
  - Content Panel
    - Module Content (dynamically loaded)
    - Progress Indicator
  - Tools Panel
    - Notes Tool
    - Timer Tool
    - Resource Library
  - Footer Panel
    - Save Button
    - End Session Button

- Systems
  - SmartStepsManager
  - SessionManager
  - ModuleManager
  - InteractionRecorder
```

## Assessment Scene

```
- Canvas (Assessment UI)
  - Header Panel
    - Assessment Title
    - Progress Indicator
  - Question Panel
    - Question Text
    - Response Options
    - Navigation Controls
  - Summary Panel (shown at end)
    - Score Display
    - Interpretation
    - Recommendations
  - Footer Panel
    - Save Button
    - Exit Button

- Systems
  - SmartStepsManager
  - AssessmentManager
  - ResponseRecorder
```

## Reports Scene

```
- Canvas (Reports UI)
  - Header Panel
    - Report Title
    - Date Range Selector
  - Filter Panel
    - Client Selector
    - Report Type Selector
    - Parameter Controls
  - Report Display
    - Charts and Graphs
    - Data Tables
    - Summary Text
  - Footer Panel
    - Export Button
    - Print Button

- Systems
  - SmartStepsManager
  - ReportGenerator
  - DataVisualizer
```

## Standard Components for All Scenes

Each scene should include:

1. **EventSystem** - For handling UI interactions
2. **SmartStepsManager** - The core singleton manager
3. **SceneSpecificManager** - Manager for scene-specific logic
4. **UI Canvas** - With consistent scaling and rendering settings
5. **LoadingOverlay** - For transition states and loading operations
6. **ErrorHandler** - For displaying errors and warnings
7. **AudioSource** - For UI sounds and feedback

## Recommended Hierarchy Organization

- Use empty GameObjects as organizational containers
- Group related UI elements under descriptive parent objects
- Keep managers at the root level for easy location
- Use consistent naming conventions:
  - Prefix UI elements with "UI_"
  - Prefix managers with "Manager_"
  - Prefix systems with "System_"

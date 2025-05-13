# Smart Steps AI End-to-End Test Report
Generated on: 2025-05-13 07:12:21

## Summary
Total tests: 7
Passed: 1
Failed: 6
Skipped: 0
Total duration: 0.03 seconds

## Test Results
### persona_loading
- Result: PASSED
- Duration: 0.00 seconds
- Details:
  - available_personas: 2
  - loaded_personas: 2

### session_creation
- Result: FAILED
- Duration: 0.01 seconds
- Details:
  - 🔴 Error: 'Session' object has no attribute 'persona_id'

### conversation_flow
- Result: FAILED
- Duration: 0.01 seconds
- Details:
  - 🔴 Error: 'PersonaManager' object has no attribute 'get_provider_info'

### session_persistence
- Result: FAILED
- Duration: 0.00 seconds
- Details:
  - 🔴 Error: Persona not found: test_persona

### persona_switch
- Result: FAILED
- Duration: 0.00 seconds
- Details:
  - 🔴 Error: SessionManager.create_session() got an unexpected keyword argument 'session_id'. Did you mean 'session_type'?

### session_analysis
- Result: FAILED
- Duration: 0.00 seconds
- Details:
  - 🔴 Error: Persona not found: test_persona

### analysis_reporting
- Result: FAILED
- Duration: 0.00 seconds
- Details:
  - 🔴 Error: Persona not found: test_persona

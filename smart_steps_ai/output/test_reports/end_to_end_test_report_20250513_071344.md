# Smart Steps AI End-to-End Test Report
Generated on: 2025-05-13 07:13:44

## Summary
Total tests: 7
Passed: 2
Failed: 5
Skipped: 0
Total duration: 0.04 seconds

## Test Results
### persona_loading
- Result: PASSED
- Duration: 0.00 seconds
- Details:
  - available_personas: 3
  - loaded_personas: 3

### session_creation
- Result: PASSED
- Duration: 0.01 seconds
- Details:
  - persona_id: professional_therapist
  - session_id: ee6f5f72-63d2-40e6-b14d-ffd938ac62d4
  - client_name: Test Client
  - persona_name: professional_therapist

### conversation_flow
- Result: FAILED
- Duration: 0.02 seconds
- Details:
  - 🔴 Error: 'Persona' object has no attribute 'provider'

### session_persistence
- Result: FAILED
- Duration: 0.00 seconds
- Details:
  - 🔴 Error: Persona not found: test_persona

### persona_switch
- Result: FAILED
- Duration: 0.01 seconds
- Details:
  - 🔴 Error: Session.add_message() missing 1 required positional argument: 'content'

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

# Smart Steps AI End-to-End Test Report
Generated on: 2025-05-13 07:16:39

## Summary
Total tests: 7
Passed: 2
Failed: 5
Skipped: 0
Total duration: 0.59 seconds

## Test Results
### persona_loading
- Result: PASSED
- Duration: 0.00 seconds
- Details:
  - available_personas: 3
  - loaded_personas: 3

### session_creation
- Result: PASSED
- Duration: 0.02 seconds
- Details:
  - persona_id: professional_therapist
  - session_id: af98a5fd-8513-4363-a01e-84e4b20f34c1
  - client_name: Test Client
  - persona_name: professional_therapist

### conversation_flow
- Result: FAILED
- Duration: 0.55 seconds
- Details:
  - 🔴 Error: 'PersonaManager' object has no attribute 'get_system_prompt'

### session_persistence
- Result: FAILED
- Duration: 0.00 seconds
- Details:
  - 🔴 Error: Persona not found: test_persona

### persona_switch
- Result: FAILED
- Duration: 0.01 seconds
- Details:
  - persona1_id: professional_therapist
  - persona2_id: behavioral_analyst
  - session_id: ff0ad42a-0729-4b52-b66a-f967d2f3353d
  - 🔴 Error: Failed to switch persona

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

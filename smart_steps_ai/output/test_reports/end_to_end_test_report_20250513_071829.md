# Smart Steps AI End-to-End Test Report
Generated on: 2025-05-13 07:18:29

## Summary
Total tests: 7
Passed: 3
Failed: 4
Skipped: 0
Total duration: 0.52 seconds

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
  - session_id: b9603280-0d67-4025-b54a-8458f2de04a9
  - client_name: Test Client
  - persona_name: professional_therapist

### conversation_flow
- Result: FAILED
- Duration: 0.47 seconds
- Details:
  - 🔴 Error: 'Session' object has no attribute 'get_messages'

### session_persistence
- Result: FAILED
- Duration: 0.00 seconds
- Details:
  - 🔴 Error: unhashable type: 'Session'

### persona_switch
- Result: PASSED
- Duration: 0.02 seconds
- Details:
  - persona1_id: professional_therapist
  - persona2_id: behavioral_analyst
  - session_id: 058467c2-5ef5-4b64-b0c7-d5402fbd493b

### session_analysis
- Result: FAILED
- Duration: 0.00 seconds
- Details:
  - 🔴 Error: unhashable type: 'Session'

### analysis_reporting
- Result: FAILED
- Duration: 0.00 seconds
- Details:
  - 🔴 Error: unhashable type: 'Session'

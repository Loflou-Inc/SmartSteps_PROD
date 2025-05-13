# Smart Steps AI End-to-End Test Report
Generated on: 2025-05-13 07:18:49

## Summary
Total tests: 7
Passed: 4
Failed: 3
Skipped: 0
Total duration: 1.07 seconds

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
  - session_id: eb524bff-6fde-4cd5-91ac-ba0af833bd07
  - client_name: Test Client
  - persona_name: professional_therapist

### conversation_flow
- Result: PASSED
- Duration: 0.97 seconds
- Details:
  - persona_id: professional_therapist
  - session_id: 161bc537-6e57-4639-bea2-27b82161f5cf
  - messages_count: 4
  - response_length: 70

### session_persistence
- Result: FAILED
- Duration: 0.01 seconds
- Details:
  - session_id: 325ca805-fce1-4524-ad7f-32fdf35d8765
  - 🔴 Error: Failed to retrieve session

### persona_switch
- Result: PASSED
- Duration: 0.04 seconds
- Details:
  - persona1_id: professional_therapist
  - persona2_id: behavioral_analyst
  - session_id: 723b2b7e-1db2-402e-a820-04a9d46d4fd7

### session_analysis
- Result: FAILED
- Duration: 0.02 seconds
- Details:
  - session_id: 40029f82-5793-4968-86ea-d50543688efb
  - 🔴 Error: Failed to analyze session

### analysis_reporting
- Result: FAILED
- Duration: 0.02 seconds
- Details:
  - session_id: 055c03ef-b455-43f0-a841-fcf633f91366
  - 🔴 Error: Failed to analyze session

%% Memory Retrieval Process
sequenceDiagram
    participant C  as Client
    participant J  as Jane_AI
    participant Cache as Context_Cache
    participant JM as Jane_Memory
    participant CM as Client_Memory
    participant KB as Knowledge_Base
    participant San as Sanitizer
    participant V  as Validator
    participant Sum as Summarizer

    C->>J: Ask question
    J->>Cache: Check hot context
    Cache-->>J: Cache hit/miss
    alt Cache miss
        J->>JM: Check Jane’s canonical & generated memories
        JM-->>J: Relevant memories
        J->>CM: Check client disclosure history
        CM-->>J: Previous disclosures
        J->>KB: Search knowledge base
        KB-->>San: Research context
        San-->>J: PII-scrubbed context
    end

    J->>J: Generate draft response
    J->>V: Validate new information
    V-->>J: Consistency result

    alt Consistent
        J->>JM: Save new generated memories (quarantined)
    else Inconsistent
        J->>J: Revise or flag for human review
    end

    J->>CM: Save new client disclosures
    J->>Sum: Summarize session
    Sum-->>CM: Store summary

    J->>C: Deliver response

    alt Retrieval timeout
        J->>C: Graceful fallback response
    end

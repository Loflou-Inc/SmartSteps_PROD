%% Memory System Architecture
flowchart TD
    subgraph secure_zone["Secure Zone"]
        subgraph stores["Datastores"]
            JM[Jane Memory Store]
            CM[Client Memory Store]
            KB[Research Knowledge Base]
            AT[Audit Trail (append-only)]
        end
    end

    Auth[AuthN/AuthZ Gateway] --> secure_zone

    A[Client Message] --> Auth
    Auth --> B{Message Type?}

    B -->|About Jane| C[Check Jane Memory]
    C --> C1{Exact Match?}
    C1 -->|Yes| C2[Use Existing Memory]
    C1 -->|No|  C3[Generate New Memory]
    C3 --> CB[Quarantine Buffer]
    CB --> CC[Consistency Check]
    CC -->|Pass| PC[Promote to Canon]
    CC -->|Fail| HR[Human Review]

    B -->|About Client History| D[Check Client Memory]
    D --> D1[Retrieve Relevant Disclosures]
    D1 --> Context

    B -->|Therapeutic Question| E[Check Knowledge Base]
    E --> E1[Semantic Search]
    E1 --> Context

    C2 --> Context
    PC --> Context

    Context[Rank & Dedup Context] --> RF[Response Formatter]
    RF --> Resp[Deliver Response]

    PC --> AT
    D1 --> CMupd[Save / Update Client Disclosures]
    CMupd --> AT

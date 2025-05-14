%% Memory Data Model
classDiagram
    class Memory {
        +id: UUID
        +type: string
        +version: int
        +status: enum{quarantined,canon,deleted}
        +created_at: datetime
        +updated_at: datetime
        +expires_at: datetime
        +source_document: string
        +source_page: int
        +llm_model: string
        +human_editor: string
        +needs_encryption: boolean
        +content: JSON
    }

    class JaneMemory {
        +topic: string
        +related_topics: string[]
        +contradicts: UUID[]
        +supports: UUID[]
        +detailed_content: JSON
    }

    class ClientMemory {
        +client_id: UUID
        +disclosure_type: string
        +sensitivity_level: int
        +topics: string[]
        +disclosed_at: datetime
        +session_number: int
    }

    class KnowledgeChunk {
        +source_document: string
        +page_number: int
        +topics: string[]
        +embedding: float[]
        +content: string
    }

    class Session {
        +id: UUID
        +client_id: UUID
        +date: datetime
        +topics_discussed: string[]
        +summary: JSON
    }

    Memory <|-- JaneMemory
    Memory <|-- ClientMemory
    Memory <|-- KnowledgeChunk
    ClientMemory "0..*" -- "0..*" Session

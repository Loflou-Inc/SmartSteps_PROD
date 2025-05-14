%% Implementation Roadmap
gantt
    title Smart Steps Memory System Implementation
    dateFormat  YYYY-MM-DD

    section Phase 0
    Define schema & validator prompt      :a1, 2025-05-15, 1w
    HIPAA/GDPR data-flow mapping          :a2, after a1, 4d

    section Phase 1
    JSON store implementation             :b1, after a2, 2w
    Basic retrieval system                :b2, after a2, 2w
    LLM eval harness & dashboards         :b3, after a2, 5d

    section Phase 2
    Contradiction checker                 :c1, after b2, 1w
    Quarantine buffer                     :c2, after c1, 3d

    section Phase 3
    Vector embeddings                     :d1, parallel with b3, 1w
    Hybrid search (BM25 + vector)         :d2, after d1, 1w
    Admin panel development               :d3, parallel with d2, 2w

    section Phase 4
    Session summarizer                    :e1, after d3, 4d
    Nightly health checks                 :e2, after e1, 3d

    section Phase 5
    Graph DB migration                    :f1, after e2, 2w
    Data-pump & backfill tests            :f2, after f1, 4d
    Role-based access                     :f3, after f1, 1w

    section Phase 6
    Load testing                          :g1, after f3, 3d
    Security audit                        :g2, after g1, 4d
    Documentation                         :g3, after g2, 3d

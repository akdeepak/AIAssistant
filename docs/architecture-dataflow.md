# AI Assistant — Data Flow (Ingest + Query)

```mermaid
flowchart LR
    subgraph INGEST_FLOWS["Ingestion Flows"]
        direction TB
        F1["POST /faqs/ingest<br/>(directory path)"]
        F2["POST /ai-assistant/catalyze<br/>(file upload)"]
        F3["POST /knowledge-bases/ingest<br/>(directory path)"]
    end

    subgraph QUERY_FLOWS["Query Flows"]
        direction TB
        Q1["POST /faqs/query"]
        Q2["POST /ai-assistant/query"]
        Q3["POST /knowledge-bases/{id}/query"]
    end

    subgraph PIPELINE1["LangChain Pipeline"]
        direction TB
        LC_LOAD["DirectoryLoader<br/>(PDF + DOCX)"]
        LC_CHUNK["RecursiveCharacter<br/>TextSplitter"]
        LC_SER["_AzureCoreEmbeddings"]
    end

    subgraph PIPELINE2["LlamaIndex Pipeline"]
        direction TB
        LI_PARSE["Smart PDF Parser<br/>(auto strategy)"]
        LI_CHUNK["SemanticSplitter /<br/>DefaultIndexBuilder"]
        LI_SER["AzureOpenAIEmbedding"]
    end

    subgraph SHARED["Shared Core"]
        direction TB
        AZ["Azure OpenAI<br/>text-embedding-ada-002"]
        QD[("Qdrant")]
    end

    F1 --> LC_LOAD --> LC_CHUNK --> LC_SER
    F2 --> LI_PARSE --> LI_CHUNK --> LI_SER
    F3 --> LC_LOAD

    LC_SER -->|same deployment| AZ
    LI_SER -->|same deployment| AZ

    AZ -->|vectors| QD

    Q1 -->|embed query| AZ
    Q1 -->|similarity search| QD
    Q2 -->|query engine| QD
    Q3 -.->|broken connector| QD

    classDef shared fill:#2563eb,color:#fff
    classDef broken fill:#ef4444,color:#fff
    class AZ,QD shared
    class F3,Q3 broken
```

## Notes

- **Blue** nodes = Shared infrastructure (Azure OpenAI + Qdrant)
- **Red** nodes = Broken / non-functional endpoints (`/knowledge-bases/` routes use `VectorDBConnector` which returns `None`)
- Both pipelines converge on the same Azure OpenAI embedding deployment, producing identical vectors

# Tài Liệu Chi Tiết Database Schema của Letta

Tài liệu này cung cấp mô tả chi tiết về từng bảng trong cơ sở dữ liệu PostgreSQL của dự án Letta, kèm theo biểu đồ quan hệ (ERD).

## 1. Core Entities (Thực thể Cốt lõi)

Nền tảng của hệ thống multi-tenant.

```mermaid
erDiagram
    organizations ||--o{ users : "has members"
    organizations ||--o{ agents : "owns"
    organizations {
        string id PK
        string name "Tenant Name"
        boolean privileged_tools "Allow specialized tools"
    }
    users {
        string id PK
        string name "User Name"
        string organization_id FK
    }
```

| Bảng | Chức năng | Các cột quan trọng |
| :--- | :--- | :--- |
| **`organizations`** | Đại diện cho một tenant hoặc tổ chức. Mọi dữ liệu (agent, user, source) đều thuộc về một organization cụ thể. | `id` (PK), `name`, `privileged_tools` (quyền chạy tool đặc biệt). |
| **`users`** | Người dùng cuối hoặc thành viên trong tổ chức. | `id` (PK), `name`, `organization_id` (FK). |

## 2. Agents System (Hệ thống Agent)

Lưu trữ trạng thái, cấu hình và danh tính của AI Agent.

```mermaid
erDiagram
    agents ||--o{ agents_tags : "tagged with"
    agents ||--o{ agent_environment_variables : "has env vars"
    agents }|--|| identities_agents : "linked to"
    identities ||--|{ identities_agents : "defines"
    groups ||--|{ groups_agents : "manages"
    groups_agents }|--|| agents : "member"

    agents {
        string id PK
        string name
        string system "System Prompt"
        json llm_config "Model Settings"
        json message_ids "Context Window State"
    }
    identities {
        string id PK
        string name
        json properties "Identity Traits"
    }
    agent_environment_variables {
        string key
        string value
        string agent_id FK
    }
    groups {
        string id PK
        string manager_type "Manager Logic"
    }
```

## 3. Memory Systems (Hệ thống Bộ nhớ)

Letta chia bộ nhớ thành 2 loại chính: **Block Memory** (Bộ nhớ lõi/ngắn hạn) và **Archival Memory** (Bộ nhớ lưu trữ/dài hạn).

### A. Block Memory (Core Memory)
Lưu trữ thông tin luôn nằm trong context window của LLM.

```mermaid
erDiagram
    agents ||--o{ blocks_agents : "uses"
    block ||--o{ blocks_agents : "assigned to"
    block ||--o{ block_history : "logs changes"
    
    block {
        string id PK
        string label "e.g. persona, human"
        string value "Text Content"
        int limit "Char Limit"
    }
    block_history {
        string id PK
        string old_value
        string new_value
        string actor_id "Who changed it"
    }
    blocks_agents {
        string agent_id FK
        string block_id FK
    }
```

### B. Archival Memory (RAG / Vector Store)
Lưu trữ dữ liệu lớn, được truy xuất qua vector search.

```mermaid
erDiagram
    archives ||--o{ archival_passages : "contains"
    archives ||--o{ archives_agents : "accessible by"
    agents ||--o{ archives_agents : "reads/writes"
    archival_passages ||--o{ passage_tags : "tagged"

    archives {
        string id PK
        string vector_db_provider "pgvector/pinecone"
    }
    archival_passages {
        string id PK
        string text "Chunk Content"
        vector embedding "Vector(4096)"
    }
    archives_agents {
        string agent_id FK
        string archive_id FK
    }
```

## 4. Resources: Sources & Files (Tài nguyên dữ liệu)

Quản lý dữ liệu bên ngoài (File upload) để nạp vào bộ nhớ.

```mermaid
erDiagram
    sources ||--o{ files : "group of"
    files ||--o{ source_passages : "chunked into"
    files ||--o{ file_contents : "extracted text"
    agents }|--|| sources_agents : "reads source"
    sources }|--|| sources_agents : "attached to"

    sources {
        string id PK
        string name "Knowledge Base Name"
    }
    files {
        string id PK
        string file_path
        string processing_status "Embed Status"
    }
    source_passages {
        string id PK
        string text
        vector embedding "RAG Vector"
    }
```

## 5. Execution & Tracing (Thực thi & Giám sát)

Theo dõi quá trình hoạt động, suy luận và gọi công cụ của Agent.

```mermaid
erDiagram
    runs ||--o{ steps : "consists of"
    runs ||--|| run_metrics : "measured by"
    runs }|--|| agents : "executed by"
    steps ||--o{ provider_traces : "logs raw API"
    
    runs {
        string id PK
        string status "running/completed"
        string stop_reason
    }
    steps {
        string id PK
        string model "Model Used"
        int total_tokens "Token Usage"
        string status "step status"
    }
    jobs {
        string id PK
        string job_type "Background Task"
        string status
    }
```

## 6. Tools & Sandbox (Công cụ & Môi trường chạy code)

Quản lý khả năng mở rộng của Agent qua Tool và môi trường thực thi an toàn.

```mermaid
erDiagram
    tools ||--o{ tools_agents : "available to"
    agents ||--o{ tools_agents : "can call"
    sandbox_configs ||--o{ sandbox_environment_variables : "params"

    tools {
        string id PK
        string name "Function Name"
        string source_code "Python Code"
        json json_schema "Input Schema"
    }
    sandbox_configs {
        string id PK
        string type "E2B/Modal/Local"
        json config "Docker/Image settings"
    }
```

## 7. Model Context Protocol (MCP)

Hỗ trợ chuẩn MCP để kết nối Agent với các thế giới dữ liệu bên ngoài.

```mermaid
erDiagram
    mcp_server ||--o{ mcp_tools : "provides"
    organizations ||--o{ mcp_server : "configures"
    
    mcp_server {
        string id PK
        string server_url
        string server_type "stdio/websocket"
    }
    mcp_tools {
        string id PK
        string tool_id "Tool Name"
    }
```

## 8. Providers Interface (Kết nối LLM)

Cấu hình các nhà cung cấp mô hình ngôn ngữ.

```mermaid
erDiagram
    providers ||--o{ provider_models : "offers"
    
    providers {
        string id PK
        string provider_type "openai/anthropic"
        string base_url "Endpoint"
    }
    provider_models {
        string id PK
        string model_type "llm/embedding"
        int context_window "Max Context"
    }
```

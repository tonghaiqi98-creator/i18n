# Architecture

公开版架构保留系统设计和工程取舍，隐藏真实平台、接口、字段和业务数据。

## System View

```mermaid
flowchart TB
    subgraph Input["Input Layer"]
        A1[Content Request]
        A2[Optional Existing Key]
        A3[Language Scope]
        A4[Length and Placeholder Constraints]
    end

    subgraph Plan["Plan Layer"]
        B1[Request Parser]
        B2[Task Router]
        B3[Model and Worker Policy]
    end

    subgraph Act["Act Layer"]
        C1[Key Generator]
        C2[Glossary Retriever]
        C3[Translator]
        C4[Cultural Adapter]
        C5[Format Normalizer]
    end

    subgraph Eval["Evaluation Layer"]
        D1[Rule Validator]
        D2[LLM-as-a-Judge]
        D3[Stress Test Suite]
        D4[Badcase Logger]
    end

    subgraph Delivery["Delivery Layer"]
        E1[Delivery Adapter]
        E2[Post-write Verification]
        E3[Human Review Checkpoint]
    end

    A1 --> B1
    A2 --> B1
    A3 --> B1
    A4 --> B1
    B1 --> B2
    B2 --> C1
    B2 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> C5
    C1 --> D1
    C5 --> D1
    D1 --> D2
    D2 --> E1
    D1 --> D4
    D2 --> D4
    D4 --> C2
    D4 --> B3
    E1 --> E2
    E2 --> E3
```

## Why This Split

Planner 只做任务拆解和路由，不直接处理翻译质量。Workers 专注生成候选结果。Evaluation Gate 先跑确定性规则，再跑语义评测，避免用 LLM 处理占位符缺失、key 非法这类可以精确判断的问题。Delivery Adapter 被单独隔离，因为它最容易绑定具体企业平台，公开版只保留边界。

## Evaluation Flow

```mermaid
sequenceDiagram
    participant P as Planner
    participant W as Worker
    participant R as Rule Validator
    participant J as Judge
    participant B as Badcase Logger
    participant D as Delivery Adapter

    P->>W: Build task with constraints
    W->>R: Return candidate output
    R-->>W: Retry with deterministic feedback
    R->>J: Pass rule-clean candidate
    J-->>B: Log low-score case
    J->>D: Approve high-confidence output
    D-->>P: Return delivery status
```

## Public Repository Boundary

```mermaid
flowchart LR
    A[Public Portfolio Repo] --> B[Anonymized Docs]
    A --> C[Sample Request]
    A --> D[Rule-based Demo Code]
    A --> E[Architecture Diagrams]

    F[Private Archive] -.excluded by gitignore.-> G[Raw Data]
    F -.excluded by gitignore.-> H[Internal Platform Details]
    F -.excluded by gitignore.-> I[Project-specific Materials]
    F -.excluded by gitignore.-> J[Interview Prep Notes]
```

## Main Design Decisions

| Decision | Reason |
|---|---|
| Put key generation behind Planner routing | Missing key is an input-shape problem, not a translation problem |
| Keep deterministic checks before LLM judging | Placeholders, naming format and length limits should be exact |
| Separate Delivery Adapter | Real upload logic is platform-specific and should not leak into public code |
| Keep badcase feedback as a first-class loop | Quality improves only when failures update glossary, prompt and tests |
| Publish anonymized sample code only | Portfolio value comes from architecture and judgment, not internal data exposure |

# Architecture Diagram

```mermaid
flowchart LR
    U[User Client] -->|User query| A[app.py]
    A --> M[Input Interceptor Middleware]
    A --> S[Conversation State / Memory Storage]
    A --> B[CompanyResearchAgent]
    B --> |Inherits| Y[AgentCoreBase]
    Y --> |users| L
    B --> |Calls| O[OpenAI model without search tool]
    B --> |Calls| W[OpenAI model with search tool]
    A --> |uses| L[Logger]
    L --> |logs to| X[bot.log file]
    T[Testing suite] --> B

    A -->|Workflow steps| R[Data Collection / Analysis / Report Generation]
    R --> B
    B -->|Responses| A
    A -->|Bot response| U
```

## Components

- app.py: Main entry point for the bot application, workflow routing, and middleware.
- agent_core/company_research_agent.py: Core AI logic for company research, analysis, and report generation.
- bot_logging.py: Centralized logging for diagnostics and monitoring.
- Conversation State / Memory Storage: Maintains workflow context across turns.
- Testing: Unit tests validate the research agent behavior.

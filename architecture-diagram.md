# 🗺️ Architecture Diagram

```mermaid
flowchart LR
    U["👤 User Client"] -->|💬 User query| A["📄 app.py"]
    A --> M["🛡️ Input Interceptor Middleware"]
    M --> A
    A --> S["🧠 Conversation State / Memory Storage"]
    A --> B["🤖 CompanyResearchAgent"]
    B --> |🔁 Inherits| Y["🧩 AgentCoreBase"]
    Y --> |📝 uses| L["📜 Logger"]
    A --> |📝 uses| L

    subgraph OpenAICloud["☁️ OpenAI Cloud"]
        O["🤖 OpenAI model without search tool"]
        W["🔍 OpenAI model with search tool"]
    end

    B -->|📡 Calls| O
    B -->|📡 Calls| W
    L --> |🗂️ logs to| X["📄 bot.log file"]
    T["🧪 Testing suite"] --> B

    A -->|🔄 Workflow steps| R["📊 Data Collection / Analysis / Report Generation"]
    R --> B
    B -->|📤 Responses| A
    A -->|💬 Bot response| U
```

## 🧩 Components

- 📄 app.py: Main entry point for the bot application, workflow routing, and middleware.
- 🤖 CompanyResearchAgent: Core AI logic for company research, analysis, and report generation. Communicates with the cloud-based OpenAI model through the SDK.
- 📜 Logger: Centralized logging for diagnostics and monitoring.
- 🧠 Conversation State / Memory Storage: Maintains workflow context across turns.
- 🧪 Testing: Unit tests validate the research agent behavior.
- 🛡️ Input Interceptor Middleware: Validates user input.
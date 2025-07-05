# CodeMentorAI

![AI Mentor](https://img.shields.io/badge/AI_Mentor-FF6F00?style=for-the-badge&logo=openai&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)
![LangChain](https://img.shields.io/badge/LangChain-00AC47?style=for-the-badge&logo=langchain&logoColor=white)

An AI-powered coding mentor that analyzes solutions and provides personalized learning paths.

## System Overview

### AI Analysis Engine
- **Core Functionality**: Code quality assessment and learning recommendations
- **Model**: Llama-3.1-8B-Instruct (HuggingFace)
- **Key Features**:
  - Pattern recognition in code
  - Knowledge gap identification
  - Adaptive learning recommendations
  - Multi-language support (Python/Java/C++)

### Web Interface
- **Core Functionality**: Interactive code analysis dashboard
- **State Management**: Streamlit session state
- **Key Features**:
  - Real-time code analysis
  - Resource recommendations (YouTube/Articles)
  - Progress tracking
  - Sample code loader

## Unified Architecture

```mermaid
graph TD
    A[User Code Input] --> B[Streamlit UI]
    B --> C[LangChain Processor]
    C --> D[HuggingFace LLM]
    D --> E[Analysis Results]
    E --> F[Personalized Recommendations]
    F --> B
    style A fill:#FF4B4B,stroke:#fff
    style B fill:#FF4B4B,stroke:#fff
    style C fill:#00AC47,stroke:#fff
    style D fill:#FFD21E,stroke:#000
    style E fill:#3776AB,stroke:#fff
    style F fill:#FF6F00,stroke:#fff

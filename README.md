# cs194-280

Welcome to MindMates
## Problem Statement
Despite significant advancements in AI-driven mental health solutions, existing systems remain limited in their approach to long-term, personalized patient care. Most current systems focus solely on providing instant responses, primarily relying on datasets of mental health counseling conversations fine-tuned for large language models. Critically, these systems do not collect or retain a patient’s contextual or longitudinal data, failing to address the long-term complexities of mental health care.

Additionally, mental health AI systems lack integration with real-world clinical infrastructure, such as Electronic Health Records (EHRs). This disconnect not only reduces their potential utility for healthcare providers but also excludes valuable data that could enhance patient care, such as treatment timelines, emotional event tracking, and actionable insights for professionals.

The lack of memory pool systems for context-aware engagement, proactive intervention strategies, and integration with clinical data highlights an urgent need for a holistic, innovative approach. To address this gap, we propose an AI system that combines domain-specific agents, persistent memory management, and EHR integration to enable proactive and personalized mental health care. However, implementing this solution raises challenges, such as preserving user privacy (e.g., compliance with HIPAA) and handling sensitive medical information securely.

## Installation
`conda create -n MindMates python=3.12`

Mac/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`

Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

`uv tool install crewai`

`cd mindmates/`

`crewai install`

## Running MindMates
(inside MindMates Conda environment)
`python src/gram_test.py`

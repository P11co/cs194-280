# cs194-280

Welcome to MindMates
## Problem Statement
Despite significant advancements in AI-driven mental health solutions, existing systems remain limited in their approach to long-term, personalized patient care. Most current systems focus solely on providing instant responses, primarily relying on datasets of mental health counseling conversations fine-tuned for large language models. Critically, these systems do not collect or retain a patient’s contextual or longitudinal data, failing to address the long-term complexities of mental health care.

Additionally, mental health AI systems lack integration with real-world clinical infrastructure, such as Electronic Health Records (EHRs). This disconnect not only reduces their potential utility for healthcare providers but also excludes valuable data that could enhance patient care, such as treatment timelines, emotional event tracking, and actionable insights for professionals.

The lack of memory pool systems for context-aware engagement, proactive intervention strategies, and integration with clinical data highlights an urgent need for a holistic, innovative approach. To address this gap, we propose an AI system that combines domain-specific agents, persistent memory management, and EHR integration to enable proactive and personalized mental health care. However, implementing this solution raises challenges, such as preserving user privacy (e.g., compliance with HIPAA) and handling sensitive medical information securely.

## Installation
1. Clone the Repository

`git clone https://github.com/P11co/cs194-280.git`

2. Set Up Poetry Environment

`poetry env use python3.12`

`poetry install`

3. Install CrewAI, used for the multi-agent framework implementation:

`poetry add "crewai<0.13,>=0.10" `

4. Set Up Ollama Models

Download the required models for local inference:

`ollama pull hf.co/CompendiumLabs/bge-base-en-v1.5-gguf `

`ollama pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF`

5. Configure Environment Variables

Create a .env file in the src/ directory with the following content:

`GEMINI_API_KEY=replace_your_gemini_api_key_here`

`BOT_TOKEN=replace_your_telegram_bot_token_here`

To get your Telegram bot token, create a new bot with @BotFather on Telegram.

## Running MindMates
Run ollama

In telegram, send `/start` to the bot you created

`python src/gram_test.py`
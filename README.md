# Chatbot Resume (Rahul Kashyap)

A minimal Gradio chatbot that roleplays as Rahul Kashyap using an OpenAI model. It pulls context from a PDF resume and a short summary, supports tool calls to record user contact details or unknown questions (via Pushover notifications), and enforces concise safety guardrails.

## Features
- Gradio ChatInterface with title, description, and example prompts
- OpenAI chat with function-call tools:
  - `record_user_details(email, name, notes)` → sends a Pushover notification
  - `record_unknown_question(question)` → sends a Pushover notification
- Safety guardrails in the system prompt (refuse sexual, harassing, abusive, illegal, dangerous, etc.)
- Loop guard to cap consecutive OpenAI calls at 15

## Requirements
- Python 3.9+
- Recommended: uv for fast installs and runs

## Quickstart
```bash
# Go to project directory
cd /Users/rahul/Downloads/work/projects/chatbot_resume

# Create venv and install deps (uv)
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Or run without activating venv
uv run pip install -r requirements.txt

# Run the app
uv run app.py
```

## Environment Variables (.env)
Create a `.env` file in the project root:
```env
# OpenAI
OPENAI_API_KEY=sk-...
# Optional if using default
# OPENAI_BASE_URL=https://api.openai.com/v1

# Pushover (optional, required for notifications)
PUSHOVER_TOKEN=your_app_token
PUSHOVER_USER=your_user_key
```

## Content Sources
- `Rahul Kashyap-DS-Resume.pdf` — parsed at startup using `pypdf`
- `rk_summary.txt` — included verbatim in the system prompt

Ensure the files exist in the project root or update paths in `app.py`.

## Usage Tips
- Ask about Rahul’s background, projects, tools, and experience.
- To share contact details, use the template:
  `Need to contact Rahul Kashyap, my email id: <your email>, note: <optional note>`
- The assistant records details via `record_user_details` and notifies via Pushover.

## Safety Guardrails (enforced)
Refuse and redirect away from:
- Sexual/explicit content; harassment, hate, abuse; violence/graphic gore; self-harm
- Illegal activities; weapons construction; malware/hacking; extremist praise
- Professional medical/legal/financial advice
The assistant briefly declines and redirects to professional, career-related topics.

## Configuration
- Model: currently `gpt-4o-mini` in `app.py` (can be made env-driven).
- Max consecutive API calls: 15 (see `Me.chat`).
- Gradio UI: title, description, examples, theme, and placeholder at the bottom of `app.py`.

## Troubleshooting
- If `ChatInterface` keyword errors occur, your Gradio version differs. We use widely supported args. Check:
  ```bash
  uv run python -c "import gradio as gr; print(gr.__version__)"
  ```
- If resume parsing prints warnings like "Ignoring wrong pointing object", they come from `pypdf` and are usually safe.
- Ensure `.env` is loaded and `OPENAI_API_KEY` is set.

## License
Personal portfolio/demo use.

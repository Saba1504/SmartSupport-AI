# SmartSupport AI — AI Workflow Automation Prototype

A portfolio-ready prototype for AI-assisted customer-support operations. It demonstrates ticket triage, priority detection, sentiment labels, response drafting, lightweight retrieval from support notes, CSV batch analysis, human review, escalation, and a dashboard.

## Features
- Single-ticket analysis.
- Optional live LLM mode using the OpenAI API.
- Offline demo mode using transparent keyword rules (not falsely presented as AI).
- Lightweight local retrieval over sample support notes.
- CSV batch processing and downloadable results.
- Human approval/editing and escalation.
- Dashboard for reviewed tickets.

## Run locally
1. Install Python 3.10+.
2. Create and activate a virtual environment (recommended).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   streamlit run app.py
   ```
5. For live AI, enter your API key in the sidebar. The key is not stored in project files. API usage may incur charges. Without a key, the app runs in demo mode.

## Batch CSV format
Required column: `customer_message`  
Optional column: `ticket_id`

Example:
```csv
ticket_id,customer_message
T-101,"My order is late and tracking has not changed."
T-102,"I was charged twice. Please help urgently."
T-103,"I cannot log in after resetting my password."
```

## Important limitations
- This is a demonstration, not a production support system.
- Demo-mode rules are a baseline and can misclassify ambiguous messages.
- Retrieval is a small keyword-overlap baseline, not a vector database.
- Do not upload real customer personal or confidential data.
- AI outputs can be wrong and must be reviewed by a person.
- The app does not send emails or customer messages.
- Do not claim performance gains unless you run and document a valid evaluation.

## Suggested evaluation
Use `evaluation/test_tickets.csv` and compare the model's category/priority predictions against the labelled expected values. Report category accuracy and priority accuracy only after running the test. Keep ambiguous cases documented rather than silently changing labels.

## Project structure
- `app.py` — Streamlit application.
- `requirements.txt` — dependencies.
- `prompts/prompt_documentation.md` — prompts, revisions, and rationale.
- `evaluation/test_tickets.csv` — small labelled test set for manual evaluation.
- `evaluation/evaluate_demo.py` — baseline evaluation script.
- `video_presentation_script.md` — 2–3 minute presentation script.
- `sample_tickets.csv` — safe, fictional example input.

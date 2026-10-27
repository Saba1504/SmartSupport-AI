# Video Presentation Script (approximately 2–3 minutes)

Hi, my name is Saba, and this is my project, SmartSupport AI, an AI-assisted customer-support workflow automation prototype.

The problem I wanted to address is that support teams receive many messages and need to understand each issue, prioritise urgent requests, and prepare consistent replies. Doing these steps manually can be repetitive, so I built a small tool to assist the team while keeping a person in control.

I used Python and Streamlit to build the web application. I included an optional LLM integration for structured ticket analysis, Pandas for CSV processing, and a small local support-reference set. The retrieval step is intentionally a simple keyword-overlap baseline, not a production vector database. The app also has a demo mode that works without an API key; that mode uses transparent rules and is not presented as AI.

My prompt-engineering approach was iterative. First, I defined the basic task: categorise a ticket and draft a reply. Then I made the output schema explicit by restricting the available categories and priority labels. Next, I added rules to prevent invented actions and unsafe requests for passwords, one-time codes, or full payment-card details. I also added escalation instructions for security-related and urgent access issues. Finally, I supplied relevant support notes as context and instructed the model not to treat them as proof that an action had occurred.

I will now demonstrate the workflow. I enter a sample customer message, analyse it, and review the suggested category, priority, summary, and reply. I can edit the reply, approve it, or mark it for escalation. Nothing is sent automatically. I can also upload a CSV of sample tickets, analyse the batch, and download the results. The dashboard shows the tickets I reviewed and their category and priority distributions.

One challenge is that AI can misclassify vague messages or generate an unsuitable response. I addressed this with constrained labels, structured output, explicit safety instructions, a human-review step, and a labelled test set for evaluation. The next improvement would be to run a documented error analysis and, if justified, replace the simple retrieval baseline with embeddings and a vector store.

The outcome is a working prototype that demonstrates practical AI integration, prompt design, basic retrieval, batch processing, and human-in-the-loop automation. Thank you for watching.

## Recording checklist
- Show the app title and explain the problem.
- Show one ticket analysis and explain the labels.
- Edit a draft and demonstrate approval or escalation.
- Show CSV batch processing and the dashboard.
- Mention that live AI requires an API key and that demo mode uses rules.
- Do not show your API key, private data, or account details.
- Only claim metrics you actually measured.

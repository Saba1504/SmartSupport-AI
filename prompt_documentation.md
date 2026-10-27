# Prompt Documentation — SmartSupport AI

## Purpose
This document records the prompts used to design the SmartSupport AI workflow and the prompt used in the application. Keep this document honest: it records the development prompts used as a project specification and the actual runtime prompt. If you use additional AI tools while developing, add the exact prompts and note what changed.

## Development prompt 1 — initial scope
> Build a Python Streamlit prototype for customer-support ticket automation. It should classify messages, assign priority and sentiment, summarise the issue, and draft a reply. Include a dashboard and CSV upload. Make it easy to run locally.

**Limitation noticed:** This scope does not specify output consistency, privacy boundaries, escalation rules, or human review.

## Development prompt 2 — structured outputs
> Improve the design so every ticket result has fixed fields: category, priority, sentiment, summary, draft_reply, and rationale. Restrict category to Refunds, Account access, Shipping, Technical issue, Billing, or General inquiry. Restrict priority to High, Medium, or Low. Explain how invalid or missing information should be handled.

**Change:** Added allowed labels and a predictable schema to make results easier to review and evaluate.

## Development prompt 3 — safety and human review
> Add safeguards for a customer-support assistant. It must not invent policy details, claim an action was completed, or request passwords, OTPs, CVVs, or full payment-card details. Escalate possible fraud, security incidents, data breaches, account lockouts, and urgent access failures. Require a human to edit and approve drafts; never send messages automatically.

**Change:** Added explicit safety rules, an escalation path, and reviewer controls.

## Development prompt 4 — retrieval grounding
> Add a lightweight retrieval step that selects the most relevant entries from a small support-reference knowledge base and includes them as context for the model. If no relevant note is found, the model must not pretend that a policy was retrieved. Clearly label this as a simple baseline rather than a production vector database.

**Change:** Added a small local reference set and transparent limitations. The current implementation uses keyword overlap, not embeddings or a vector database.

## Runtime prompt used by live AI mode
The application sends the following task instructions to the LLM (the ticket text and retrieved notes are inserted dynamically):

> You are a careful customer-support triage assistant. Analyse the ticket and return ONLY valid JSON with keys: category (one of Refunds, Account access, Shipping, Technical issue, Billing, General inquiry), priority (High, Medium, Low), sentiment (Negative, Neutral, Positive), summary (max 35 words), draft_reply (polite, specific, concise; do not claim actions were taken; ask only for information necessary; never request passwords, OTPs, CVVs, or full payment-card details), rationale (one short sentence explaining category/priority). Escalate potential fraud, security incidents, data breaches, account lockouts, and urgent access failures as High priority. Use the provided support reference notes only as guidance, not as proof of an action. If information is missing, say so rather than inventing facts. This is a draft for human review, not an automatically sent response.

The API call also includes a system instruction: “Follow the output schema exactly. Return JSON only.” Temperature is set to 0.2.

## Evaluation and iteration plan
1. Run the labelled examples in `evaluation/test_tickets.csv`.
2. Record predicted category and priority.
3. Compare predictions with the expected labels; calculate category and priority accuracy.
4. Inspect errors and ambiguous cases manually.
5. Revise the prompt only when the error analysis justifies a change.
6. Re-run the same test set and report before/after results without changing the test labels.

## Transparency note
The development prompts above are a documented design trail for this project. They should not be described as a verbatim history of prompts sent to a particular external AI tool unless you actually used them that way. Add any real prompts you use during your own development to preserve an accurate audit trail.

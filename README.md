# Legalintake-chatbot
# ⚖️ LegalIntake

An AI-assisted legal client intake application built with Streamlit. It helps law firms pre-screen inquiries, classify them into a practice area, collect client details, and schedule a consultation.

> **Disclaimer:** This is a demo / student project. It provides general information only, does not constitute legal advice, and does not create an attorney-client relationship.

## Features

- **Smart Classification** — analyzes a free-text description of a legal issue and matches it against a keyword library to suggest the most relevant practice area (Family, Criminal, Property, Employment, Corporate, Intellectual Property, Immigration), with a confidence indicator and tie detection for ambiguous cases.
- **Client Intake Form** — collects name, contact details, incident date, people/organizations involved, case description, and an optional supporting document.
- **Consultation Scheduling** — lets a client pick a preferred date, time, and consultation type (online/in-person) after completing intake.
- **Case Summary** — a consolidated view of the client's intake info, AI classification result, and consultation request for lawyer review.

## Requirements

- Python 3.9+
- [Streamlit](https://streamlit.io/)

## Installation

```bash
pip install streamlit
```

## Running the app

```bash
streamlit run legal_intake_app.py
```

This opens the app in your browser, typically at `http://localhost:8501`.

## Project structure

```
legal_intake_app.py   # Single-file Streamlit application
README.md             # This file
```

## How it works

1. **Home** — overview of the workflow and legal disclaimer.
2. **Legal Assistant** — user describes their issue in free text; a keyword-scoring classifier suggests a practice area.
3. **Client Intake** — user fills in a structured form with contact and case details.
4. **Consultation** — once intake is complete, the user picks a date/time/type for a consultation.
5. **Case Summary** — displays everything collected so far, ready for a lawyer's review.

State is held in `st.session_state` for the duration of the browser session and is not persisted to a database — this is a front-end intake demo, not a production case management system.

## Security notes

- All user-supplied text rendered via `st.markdown(..., unsafe_allow_html=True)` is HTML-escaped to prevent script injection.
- Email input is validated against a basic format pattern before submission is accepted.
- No sensitive data (passwords, financial details, government IDs) should be entered — this demo does not encrypt or securely store submissions.

## Known limitations

- Classification is keyword-based, not a trained ML/LLM model — it will miss issues phrased without matching keywords and can't reason about nuance or multi-issue cases.
- No persistent storage: refreshing the browser or restarting the app clears all submitted data.
- Consultation scheduling does not connect to a real calendar or send notifications.
- Uploaded documents are referenced by filename only; file contents are not stored or processed.

## License

Student project / prototype — no license specified.

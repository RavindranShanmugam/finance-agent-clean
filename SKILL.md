---
name: finance-spreadsheet-agent
description: >-
  Import bank statement PDFs into a categorized spending spreadsheet and answer
  questions about personal spending using a local Ollama model. Use when the user
  wants to extract transactions from a bank statement, categorize expenses, build
  or update a spending tracker, or ask what they spend the most on.
---

# Finance Spreadsheet Agent

A local, private workflow for analyzing personal spending from bank statements.
Python does all calculations; a local LLM only interprets questions and explains results.

## When to use

- The user has a bank statement (PDF) and wants it as a categorized spreadsheet.
- The user asks "what did I spend most on?", "how much on X?", or "biggest purchases?".
- The user wants a private, offline finance tracker they update each month.

## Files

- `import_statement.py` — parse a Bank of America PDF into a categorized `spending.xlsx`; re-run monthly to append new statements (de-duplicates automatically).
- `chat_agent.py` — terminal chat over `spending.xlsx`.
- `desktop_agent.py` — native desktop-window chat (Tkinter, no browser).
- `finance_agent.py` — Streamlit web UI.
- `make_sample.py` — generate sample data to test without a real statement.

## Workflow

1. Ensure Ollama is installed and a model is pulled (`ollama pull llama3.2`).
2. Install deps: `python -m pip install -r requirements.txt`.
3. Build the sheet: `python import_statement.py <statement.pdf>` (or `make_sample.py`).
4. Ask questions via any chat interface.

## Design principle

The agent exposes Python functions as tools (`total_spent`, `top_spending`,
`category_total`, `biggest_purchases`). The model chooses which tool fits the
question; Python computes the exact figure, keeping financial math accurate.

## Privacy

All processing is local. Never commit `*.pdf` or `*.xlsx` — they are git-ignored.

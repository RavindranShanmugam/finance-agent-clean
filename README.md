# Finance Spreadsheet Agent

A **local, private AI agent** that turns your bank statement PDFs into a categorized
spending spreadsheet and lets you ask questions about your money in plain English —
all running on your own machine with [Ollama](https://ollama.com). No cloud, no data leaves your computer.

> Ask *"What did I spend most on?"* and get an answer from your own bank data.

## What it does

- **Imports** a Bank of America statement PDF and extracts every transaction
- **Categorizes** merchants (coffee, dining, groceries, gas, subscriptions, …)
- **Builds & updates** a master `spending.xlsx` you can re-run each month
- **Chats** with your spending via an AI agent that picks the right tool, while Python does the math (so the numbers are always accurate)

## How it works

The agent follows a simple, reliable pattern: **the AI decides, Python calculates.**
You ask a question, a local LLM chooses which tool to run, and a plain Python
function computes the real number. The model only explains results.

```
Bank PDF  ->  import_statement.py  ->  spending.xlsx  ->  AI agent  ->  answer
```

## Setup

1. **Install [Ollama](https://ollama.com)** and pull a model:
   ```
   ollama pull llama3.2
   ```
2. **Install Python dependencies:**
   ```
   python -m pip install -r requirements.txt
   ```

## Usage

**1. Create a spending sheet.** Either import a real Bank of America PDF:
```
python import_statement.py yourstatement.pdf
```
…or generate sample data to try it out:
```
python make_sample.py
```

**2. Chat with your spending.** Pick an interface:

| Interface | Command |
|-----------|---------|
| Terminal  | `python chat_agent.py` |
| Desktop window | `python desktop_agent.py` |
| Web page  | `python -m streamlit run finance_agent.py` |

Then ask things like *"What did I spend most on?"*, *"How much on coffee?"*, *"What were my biggest purchases?"*

## Privacy

Runs **100% locally**. Your statements and `spending.xlsx` are excluded from git by
`.gitignore` so they are **never** uploaded. Before committing, confirm no `.pdf` or
`.xlsx` files are staged.

## Customizing categories

Edit the `CATEGORY_RULES` section at the top of `import_statement.py` — add merchant
names under the category you want. Unrecognized merchants are tagged "Uncategorized."

## Note

The PDF parser is tuned to **Bank of America** statement layouts. Other banks need
the `parse_statement()` function adjusted.

## License

MIT — see [LICENSE](LICENSE).

"""
finance_brain.py  -  Decides WHICH tool answers a question, then explains it.

The whole app follows one rule: the AI decides, Python calculates. This module
holds the "decide + explain" half and picks the best brain available, in order:

  1. Ollama (local llama3.2)  -> free, private, what you run while recording
  2. Claude API (if a key is set) -> for the deployed "try it yourself" version
  3. Keyword router (no LLM)   -> always works, no key, so the cloud app never 500s

Every path returns the same shape:
    (answer_text: str, tool_name: str|None, tool_args: dict, brain_label: str)
so the UI can show which tool ran and which brain answered.
"""
import os
import json

OLLAMA_MODEL = "llama3.2"
CLAUDE_MODEL = "claude-opus-4-8"  # change in secrets/env via CLAUDE_MODEL if you want cheaper

# JSON-schema tool definitions (shared by the Claude path; Ollama reads the
# Python functions' docstrings directly, so it doesn't need these).
TOOL_SCHEMAS = [
    {
        "name": "total_spent",
        "description": "Return the total amount of real spending across all categories.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "top_spending",
        "description": "Return spending broken down by category, biggest first.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "category_total",
        "description": "Return how much was spent in one category, e.g. 'Coffee', 'Dining', 'Gas', 'Subscriptions'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "A spending category or keyword"}
            },
            "required": ["category"],
        },
    },
    {
        "name": "biggest_purchases",
        "description": "Return the 5 largest individual purchases.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


# ---------- brain detection ----------
def anthropic_key():
    """Find an Anthropic key in Streamlit secrets or the environment."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get("ANTHROPIC_API_KEY")  # type: ignore[attr-defined]
    except Exception:
        return None


def ollama_ready(model=OLLAMA_MODEL):
    """True only if the Ollama server is up AND the model is pulled."""
    try:
        import ollama
        listed = ollama.list().get("models", [])
        names = [m.get("model") or m.get("name") or "" for m in listed]
        return any(model in n for n in names)
    except Exception:
        return False


def active_brain():
    """Return ('ollama'|'claude'|'keyword', label) for the best available brain."""
    if ollama_ready():
        return "ollama", f"🖥️ Local AI · Ollama ({OLLAMA_MODEL})"
    if anthropic_key():
        model = os.environ.get("CLAUDE_MODEL", CLAUDE_MODEL)
        return "claude", f"☁️ Claude ({model})"
    return "keyword", "⚡ Instant router (no LLM)"


# ---------- the three brains ----------
def _ask_ollama(question, tools):
    import ollama
    resp = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": question}],
        tools=list(tools.values()),
    )
    msg = resp["message"]
    if msg.get("tool_calls"):
        call = msg["tool_calls"][0]
        name = call["function"]["name"]
        args = call["function"]["arguments"] or {}
        result = tools[name](**args)
        final = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content":
            f"The user asked: '{question}'. Here is the real data:\n{result}\n"
            "Answer in one or two friendly sentences. Use the dollar amounts shown."}])
        return final["message"]["content"], name, args
    return msg["content"], None, {}


def _ask_claude(question, tools, key):
    import anthropic
    model = os.environ.get("CLAUDE_MODEL", CLAUDE_MODEL)
    client = anthropic.Anthropic(api_key=key)
    resp = client.messages.create(
        model=model, max_tokens=1024, tools=TOOL_SCHEMAS,
        messages=[{"role": "user", "content": question}],
    )
    tool_blocks = [b for b in resp.content if b.type == "tool_use"]
    if tool_blocks:
        tb = tool_blocks[0]
        args = dict(tb.input)  # already parsed by the SDK
        result = tools[tb.name](**args)
        final = client.messages.create(
            model=model, max_tokens=300, tools=TOOL_SCHEMAS,
            messages=[
                {"role": "user", "content": question},
                {"role": "assistant", "content": resp.content},
                {"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": tb.id, "content": result}]},
            ],
        )
        text = "".join(b.text for b in final.content if b.type == "text")
        return text.strip(), tb.name, args
    text = "".join(b.text for b in resp.content if b.type == "text")
    return text.strip(), None, {}


def _ask_keyword(question, tools, categories):
    """No LLM. Match the question to a tool by keywords — always returns an answer."""
    q = question.lower()
    if any(w in q for w in ("biggest", "largest", "most expensive", "top purchase", "biggest purchase")):
        return tools["biggest_purchases"](), "biggest_purchases", {}
    # a specific category named?
    for cat in categories:
        first = cat.split(" ")[0].lower()  # 'Coffee & Cafe' -> 'coffee'
        if first in q or cat.lower() in q:
            return tools["category_total"](cat), "category_total", {"category": cat}
    for kw, cat in (("coffee", "Coffee"), ("subscription", "Software"), ("subs", "Software"),
                    ("dining", "Fast Food"), ("food", "Fast Food"), ("grocer", "Groceries"),
                    ("gas", "Gas"), ("shop", "Shopping"), ("phone", "Phone")):
        if kw in q:
            return tools["category_total"](cat), "category_total", {"category": cat}
    if any(w in q for w in ("most", "breakdown", "category", "categories", "where", "top")):
        return tools["top_spending"](), "top_spending", {}
    return tools["total_spent"](), "total_spent", {}


# ---------- public entry point ----------
def answer(question, tools, categories):
    """Route `question` to the best available brain. Never raises to the caller."""
    brain, label = active_brain()
    try:
        if brain == "ollama":
            text, name, args = _ask_ollama(question, tools)
        elif brain == "claude":
            text, name, args = _ask_claude(question, tools, anthropic_key())
        else:
            text, name, args = _ask_keyword(question, tools, categories)
        return text, name, args, label
    except Exception as e:
        # Any brain failure (server down, bad key, rate limit) -> free router, still useful.
        text, name, args = _ask_keyword(question, tools, categories)
        return text, name, args, f"⚡ Instant router (fallback after {brain} error)"

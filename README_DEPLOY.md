# Deploying Ravs Finance Agent (so your audience can try it)

The app runs the same code three ways and auto-picks the best brain available:

| Where | Brain it uses | Cost |
|---|---|---|
| **Your laptop** (recording videos) | 🖥️ Ollama `llama3.2` | Free, private |
| **Streamlit Cloud** with no key | ⚡ Keyword router (no LLM) | Free, always works |
| **Streamlit Cloud** with an Anthropic key | ☁️ Claude | Pay-per-question |

> Ollama can't run on Streamlit Cloud, so the deployed app falls back automatically —
> it never crashes for your audience. Add a Claude key only if you want real AI in the public version.

There's **no data file to upload**: if `spending.xlsx` is missing (it's git-ignored for privacy),
the app builds the demo ledger in memory from `demo_data.py`. Same numbers everywhere.

---

## 1. Push the code to GitHub

Your repo already exists: `https://github.com/RavindranShanmugam/finance-agent-clean`

```bash
cd "OneDrive/Documents/finance-agent-clean"
git add finance_agent.py finance_brain.py demo_data.py make_demo.py \
        requirements.txt .gitignore .streamlit/config.toml .streamlit/secrets.toml.example \
        README_DEPLOY.md
git commit -m "Web build: chart, Ravs branding, cloud-ready brain (Ollama/Claude/router)"
git push origin main
```

*(`spending.xlsx`, `.env`, and `.streamlit/secrets.toml` stay out of git — they're in `.gitignore`.)*

## 2. Deploy on Streamlit Community Cloud (free)

1. Go to **https://share.streamlit.io** and sign in with GitHub.
2. **New app** → pick repo `RavindranShanmugam/finance-agent-clean`, branch `main`, main file `finance_agent.py`.
3. Click **Deploy**. You'll get a public URL like `https://ravs-finance-agent.streamlit.app`.

That's it — the public app runs on the free keyword router.

## 3. (Optional) Turn on real Claude AI in the public app

In the app's **Settings → Secrets**, paste:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
CLAUDE_MODEL = "claude-opus-4-8"   # optional; a smaller model is cheaper for a public demo
```

Save — the app restarts and the badge switches to **☁️ Claude**.
⚠️ A public app means anyone can spend your API credits. Prefer the free router for a wide launch,
or add usage caps / a cheaper model if you enable Claude.

---

## Run it locally (for recording)

```bash
python -m streamlit run finance_agent.py     # opens http://localhost:8501
```

Ollama must be running with the model pulled (`ollama pull llama3.2`). Ask a throwaway
question before you go live so the model is warm and the first real answer is fast.

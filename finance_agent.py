"""
finance_agent.py  -  Ravs Finance Agent (web).

Chat with your spending in plain English. The AI decides which tool to run;
Python does the math, so the dollar figures are always exact.

RUN LOCALLY:   streamlit run finance_agent.py     (uses Ollama - free & private)
DEPLOYED:      falls back to Claude (if a key is set) or a free keyword router,
               so the public "try it yourself" version always works.
"""
import os
import pandas as pd
import streamlit as st

import finance_brain as brain
from demo_data import demo_dataframe, NON_SPEND

MASTER = "spending.xlsx"

CATEGORY_EMOJI = {
    "Coffee & Cafe": "☕", "Fast Food / Dining": "🍔", "Groceries": "🛒",
    "Gas & Convenience": "⛽", "Shopping / Retail": "🛍️", "Software & Subs": "💳",
    "Phone": "📱", "Shipping": "📦", "Uncategorized": "❓",
}


# ---------- DATA (real xlsx if present, else the safe in-memory demo) ----------
@st.cache_data
def load_spending():
    if os.path.exists(MASTER):
        df = pd.read_excel(MASTER, sheet_name="Transactions")
        source = "spending.xlsx"
    else:
        df = demo_dataframe()          # works on Streamlit Cloud with no data file
        source = "demo data"
    spend = df[(df["Amount"] < 0) & (~df["Category"].isin(NON_SPEND))].copy()
    spend["Spent"] = spend["Amount"].abs()
    return spend, source


spend, data_source = load_spending()


# ---------- TOOLS (plain Python, exact every time) ----------
def total_spent() -> str:
    """Return the total amount of real spending across all categories."""
    return f"Total spending is ${spend['Spent'].sum():.2f}"

def top_spending() -> str:
    """Return spending broken down by category, biggest first."""
    s = spend.groupby("Category")["Spent"].sum().sort_values(ascending=False)
    return s.round(2).to_string()

def category_total(category: str) -> str:
    """Return how much was spent in one category, e.g. 'Coffee', 'Dining', 'Gas'."""
    cats = spend["Category"].unique()
    match = next((c for c in cats if category.lower() in c.lower()), None)
    if match is None:
        return f"No category matching '{category}'. Categories are: {', '.join(cats)}"
    amt = spend[spend["Category"] == match]["Spent"].sum()
    return f"You spent ${amt:.2f} on {match}"

def biggest_purchases() -> str:
    """Return the 5 largest individual purchases."""
    top = spend.sort_values("Spent", ascending=False).head(5)
    return top[["Date", "Description", "Spent"]].to_string(index=False)

TOOLS = {"total_spent": total_spent, "top_spending": top_spending,
         "category_total": category_total, "biggest_purchases": biggest_purchases}
CATEGORIES = sorted(spend["Category"].unique())


# ---------- PAGE ----------
st.set_page_config(page_title="Ravs Finance Agent", page_icon="💸", layout="wide")

st.title("💸 Ravs Finance Agent")
st.markdown(
    "**Ask your money questions in plain English.** "
    "A local AI picks the right tool — Python does the math, so the numbers are always exact."
)
if data_source == "demo data":
    st.caption("🧪 Showing demo data — nothing here is a real transaction.")

# ---- KPI tiles ----
by_cat = spend.groupby("Category")["Spent"].sum().sort_values(ascending=False)
top_cat = by_cat.index[0]
biggest = spend.loc[spend["Spent"].idxmax()]

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Total spent", f"${spend['Spent'].sum():,.2f}")
k2.metric("🧾 Transactions", f"{len(spend)}")
k3.metric(f"{CATEGORY_EMOJI.get(top_cat, '🏷️')} Top category", top_cat, f"${by_cat.iloc[0]:,.0f}")
k4.metric("🔺 Biggest purchase", biggest["Description"][:18], f"${biggest['Spent']:,.0f}")

# ---- Spending-by-category chart ----
st.subheader("📊 Where the money went")
chart_df = by_cat.rename(index=lambda c: f"{CATEGORY_EMOJI.get(c, '🏷️')} {c}").to_frame("Spent ($)")
st.bar_chart(chart_df, color="#10b981", horizontal=True)

with st.expander("🔎 See the transactions behind these numbers"):
    view = spend[["Date", "Description", "Category", "Spent"]].copy()
    view["Category"] = view["Category"].map(lambda c: f"{CATEGORY_EMOJI.get(c, '🏷️')} {c}")
    st.dataframe(view, use_container_width=True, hide_index=True)

# ---- Ask the agent ----
st.subheader("💬 Ask the agent")
_, brain_label = brain.active_brain()
st.caption(f"Brain in use: **{brain_label}**")

st.session_state.setdefault("question", "")
cols = st.columns(4)
SUGGESTIONS = [
    "What did I spend the most on?",
    "How much on coffee?",
    "What were my biggest purchases?",
    "How much on subscriptions?",
]
for col, s in zip(cols, SUGGESTIONS):
    if col.button(s, use_container_width=True):
        st.session_state["question"] = s

question = st.text_input(
    "Ask about your spending:",
    key="question",
    placeholder="e.g. What did I spend most on?",
)

if question:
    with st.spinner("Thinking..."):
        text, tool_name, tool_args, used_brain = brain.answer(question, TOOLS, CATEGORIES)
    if tool_name:
        arg_str = f"({tool_args or ''})" if tool_args else "()"
        st.info(f"🛠️ The agent ran: **{tool_name}{arg_str}**  ·  {used_brain}")
    st.success(text)

st.divider()
st.caption("Built by Ravi · Ravs Automation Agency — the AI decides, Python calculates.")

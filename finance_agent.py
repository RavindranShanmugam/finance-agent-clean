"""
finance_agent.py  -  Chat with your real spending in plain English.

WHAT IT DOES
  Reads spending.xlsx (the file import_statement.py builds) and lets you ask
  questions like "what did I spend most on?" or "how much on coffee?".
  The AI decides which tool to use; Python does the math.

RUN IT WITH:   streamlit run finance_agent.py
"""
import pandas as pd
import streamlit as st
import ollama

MASTER = "spending.xlsx"
MODEL = "llama3.2"
# Money out but NOT everyday spending (so they don't drown out the real picture):
NON_SPEND = ["Investing", "Transfers / Other", "Fees"]

# ---- LOAD THE DATA ONCE ----
df = pd.read_excel(MASTER, sheet_name="Transactions")
# "spend" = only real spending: money out, excluding investing/transfers/fees
spend = df[(df["Amount"] < 0) & (~df["Category"].isin(NON_SPEND))].copy()
spend["Spent"] = spend["Amount"].abs()

# ---- THE TOOLS (plain Python, accurate every time) ----
def total_spent() -> str:
    """Return the total amount of real spending across all categories."""
    return f"Total spending is ${spend['Spent'].sum():.2f}"

def top_spending() -> str:
    """Return spending broken down by category, biggest first."""
    s = spend.groupby("Category")["Spent"].sum().sort_values(ascending=False)
    return s.round(2).to_string()

def category_total(category: str) -> str:
    """Return how much was spent in one category, e.g. 'Coffee', 'Dining', 'Gas'."""
    # match loosely so 'coffee' finds 'Coffee & Cafe', 'gas' finds 'Gas & Convenience'
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

AVAILABLE = {
    "total_spent": total_spent,
    "top_spending": top_spending,
    "category_total": category_total,
    "biggest_purchases": biggest_purchases,
}

# ---- THE WEB PAGE ----
st.title("Finance Agent")
st.caption(f"Reading {MASTER} - {len(spend)} spending transactions")

with st.expander("See my spending data"):
    st.dataframe(spend[["Date", "Description", "Category", "Spent"]])

question = st.text_input("Ask about your spending:",
                         placeholder="e.g. What did I spend most on?")

if question:
    with st.spinner("Thinking..."):
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": question}],
            tools=[total_spent, top_spending, category_total, biggest_purchases],
        )
        msg = response["message"]

        if msg.get("tool_calls"):
            call = msg["tool_calls"][0]
            name = call["function"]["name"]
            args = call["function"]["arguments"]
            result = AVAILABLE[name](**args)
            st.info(f"The agent used: {name}({args or ''})")

            final = ollama.chat(model=MODEL, messages=[{"role": "user", "content":
                f"The user asked: '{question}'. Here is the real data:\n{result}\n"
                "Answer them in one or two friendly sentences. Use the dollar amounts shown."}])
            st.success(final["message"]["content"])
        else:
            st.success(msg["content"])

"""
chat_agent.py  -  Chat with your real spending, right in the terminal (no browser).

RUN IT WITH:   python chat_agent.py
Then type questions like:  what did I spend most on?
Type  quit  to exit.
"""
import pandas as pd
import ollama

MASTER = "spending.xlsx"
MODEL = "llama3.2"
NON_SPEND = ["Investing", "Transfers / Other", "Fees"]

# ---- LOAD DATA ----
df = pd.read_excel(MASTER, sheet_name="Transactions")
spend = df[(df["Amount"] < 0) & (~df["Category"].isin(NON_SPEND))].copy()
spend["Spent"] = spend["Amount"].abs()

# ---- TOOLS (Python does the math) ----
def total_spent() -> str:
    """Return the total amount of real spending across all categories."""
    return f"Total spending is ${spend['Spent'].sum():.2f}"

def top_spending() -> str:
    """Return spending broken down by category, biggest first."""
    return spend.groupby("Category")["Spent"].sum().sort_values(ascending=False).round(2).to_string()

def category_total(category: str) -> str:
    """Return how much was spent in one category, e.g. 'Coffee', 'Dining', 'Gas'."""
    cats = spend["Category"].unique()
    match = next((c for c in cats if category.lower() in c.lower()), None)
    if match is None:
        return f"No category matching '{category}'. Categories: {', '.join(cats)}"
    return f"You spent ${spend[spend['Category']==match]['Spent'].sum():.2f} on {match}"

def biggest_purchases() -> str:
    """Return the 5 largest individual purchases."""
    top = spend.sort_values("Spent", ascending=False).head(5)
    return top[["Date", "Description", "Spent"]].to_string(index=False)

AVAILABLE = {"total_spent": total_spent, "top_spending": top_spending,
             "category_total": category_total, "biggest_purchases": biggest_purchases}
TOOLS = [total_spent, top_spending, category_total, biggest_purchases]

# ---- CHAT LOOP ----
print(f"Finance Agent ready - {len(spend)} spending transactions loaded.")
print("Ask a question (or type 'quit' to exit).\n")

while True:
    question = input("You: ").strip()
    if question.lower() in ("quit", "exit", ""):
        print("Bye!")
        break

    response = ollama.chat(model=MODEL,
                           messages=[{"role": "user", "content": question}],
                           tools=TOOLS)
    msg = response["message"]

    if msg.get("tool_calls"):
        call = msg["tool_calls"][0]
        name = call["function"]["name"]
        args = call["function"]["arguments"]
        result = AVAILABLE[name](**args)
        print(f"  [agent used: {name}({args or ''})]")
        final = ollama.chat(model=MODEL, messages=[{"role": "user", "content":
            f"The user asked: '{question}'. Here is the real data:\n{result}\n"
            "Answer in one or two friendly sentences using the dollar amounts shown."}])
        print("Agent:", final["message"]["content"], "\n")
    else:
        print("Agent:", msg["content"], "\n")

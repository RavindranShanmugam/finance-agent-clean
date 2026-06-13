"""
desktop_agent.py  -  Chat with your spending in a native desktop window (no browser).

RUN IT WITH:   python desktop_agent.py
A window opens. Type a question, press Enter (or click Ask).
"""
import threading
import pandas as pd
import ollama
import tkinter as tk
from tkinter import scrolledtext

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

# ---- THE AGENT (runs in a background thread so the window never freezes) ----
def ask_agent(question):
    response = ollama.chat(model=MODEL,
                           messages=[{"role": "user", "content": question}],
                           tools=TOOLS)
    msg = response["message"]
    if msg.get("tool_calls"):
        call = msg["tool_calls"][0]
        name = call["function"]["name"]
        args = call["function"]["arguments"]
        result = AVAILABLE[name](**args)
        final = ollama.chat(model=MODEL, messages=[{"role": "user", "content":
            f"The user asked: '{question}'. Here is the real data:\n{result}\n"
            "Answer in one or two friendly sentences using the dollar amounts shown."}])
        return name, final["message"]["content"]
    return None, msg["content"]

# ---- THE WINDOW ----
root = tk.Tk()
root.title("Finance Agent")
root.geometry("640x520")

header = tk.Label(root, text=f"Finance Agent  -  {len(spend)} spending transactions loaded",
                  font=("Segoe UI", 11, "bold"), pady=8)
header.pack()

chat = scrolledtext.ScrolledText(root, wrap="word", font=("Segoe UI", 10),
                                 state="disabled", height=20)
chat.pack(fill="both", expand=True, padx=10, pady=(0, 6))

bottom = tk.Frame(root)
bottom.pack(fill="x", padx=10, pady=(0, 10))
entry = tk.Entry(bottom, font=("Segoe UI", 11))
entry.pack(side="left", fill="x", expand=True, ipady=4)
ask_btn = tk.Button(bottom, text="Ask")
ask_btn.pack(side="left", padx=(6, 0))

def show(speaker, text):
    chat.config(state="normal")
    chat.insert("end", f"{speaker}: {text}\n\n")
    chat.config(state="disabled")
    chat.see("end")

def on_ask(event=None):
    q = entry.get().strip()
    if not q:
        return
    entry.delete(0, "end")
    show("You", q)
    ask_btn.config(state="disabled", text="Thinking...")

    def worker():
        try:
            tool, answer = ask_agent(q)
            note = f"  [used: {tool}]" if tool else ""
        except Exception as e:
            answer, note = f"Error: {e}", ""
        def done():
            show("Agent", answer + note)
            ask_btn.config(state="normal", text="Ask")
            entry.focus()
        root.after(0, done)

    threading.Thread(target=worker, daemon=True).start()

ask_btn.config(command=on_ask)
entry.bind("<Return>", on_ask)
entry.focus()

show("Agent", "Hi! Ask me things like 'What did I spend most on?' or 'How much on coffee?'")
root.mainloop()

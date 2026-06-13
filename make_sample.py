"""Create a tiny sample spending.xlsx so you can try the agents without a real bank statement."""
import pandas as pd
data = {
    "Date": ["05/01/26","05/02/26","05/03/26","05/05/26","05/08/26","05/09/26"],
    "Description": ["STARBUCKS","FOOD LION","MCDONALDS","CIRCLE K GAS","CHATGPT SUB","SUBWAY"],
    "Amount": [-6.50,-42.10,-9.40,-55.00,-20.00,-8.25],
    "Source": ["sample"]*6,
    "Category": ["Coffee & Cafe","Groceries","Fast Food / Dining","Gas & Convenience","Software & Subs","Fast Food / Dining"],
}
pd.DataFrame(data).to_excel("spending.xlsx", sheet_name="Transactions", index=False)
print("Created sample spending.xlsx")

"""
make_demo.py  -  Write a realistic DEMO spending.xlsx for public showcases.

Uses the shared ledger in demo_data.py so the file and the app's in-memory
fallback stay identical. Nothing here is real. Run:  python make_demo.py
"""
import pandas as pd
from demo_data import demo_dataframe, NON_SPEND

df = demo_dataframe()

with pd.ExcelWriter("spending.xlsx", engine="openpyxl") as xl:
    df.to_excel(xl, sheet_name="Transactions", index=False)
    spend = df[(df["Amount"] < 0) & (~df["Category"].isin(NON_SPEND))].copy()
    spend["Spent"] = spend["Amount"].abs()
    top = spend.groupby("Category")["Spent"].sum().sort_values(ascending=False).round(2)
    top.to_frame("Total Spent").to_excel(xl, sheet_name="Top Spending")

spend = df[(df["Amount"] < 0) & (~df["Category"].isin(NON_SPEND))]
print(f"Wrote spending.xlsx  |  {len(df)} rows, {len(spend)} spending transactions, "
      f"${spend['Amount'].abs().sum():.2f} total spending (DEMO)")

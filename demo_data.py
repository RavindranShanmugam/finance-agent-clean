"""
demo_data.py  -  The realistic DEMO ledger, in one place.

Shared by make_demo.py (writes spending.xlsx) and finance_agent.py (falls back
to this in-memory when no spending.xlsx exists, e.g. on Streamlit Cloud). Same
schema import_statement.py produces, so the app treats it identically.
Nothing here is real — invented merchants and amounts, safe to show publicly.
"""
import pandas as pd

NON_SPEND = ["Investing", "Transfers / Other", "Fees"]

# (Date, Description, Amount, Category)  -- Amount negative = money out (spending)
SPENDING = [
    ("05/02/26", "BLUE BOTTLE COFFEE",        -6.75,  "Coffee & Cafe"),
    ("05/05/26", "STARBUCKS STORE #1123",     -5.45,  "Coffee & Cafe"),
    ("05/09/26", "LOCAL GRIND CARY NC",       -4.90,  "Coffee & Cafe"),
    ("05/14/26", "STARBUCKS STORE #1123",     -6.10,  "Coffee & Cafe"),
    ("05/19/26", "BLUE BOTTLE COFFEE",        -6.75,  "Coffee & Cafe"),
    ("05/23/26", "STARBUCKS STORE #1123",     -5.45,  "Coffee & Cafe"),
    ("05/03/26", "CHIPOTLE 2148",             -12.85, "Fast Food / Dining"),
    ("05/06/26", "BILTMORE GRILL RALEIGH",    -34.60, "Fast Food / Dining"),
    ("05/10/26", "PANDA EXPRESS 1877",        -11.20, "Fast Food / Dining"),
    ("05/13/26", "DOORDASH*THAI CAFE",        -28.40, "Fast Food / Dining"),
    ("05/17/26", "MCDONALDS F1204",           -9.15,  "Fast Food / Dining"),
    ("05/21/26", "THE CHEESECAKE FACTORY",    -52.30, "Fast Food / Dining"),
    ("05/24/26", "DOMINOS PIZZA 4471",        -18.75, "Fast Food / Dining"),
    ("05/04/26", "WHOLE FOODS MKT CARY",      -84.20, "Groceries"),
    ("05/11/26", "HARRIS TEETER #0281",       -63.55, "Groceries"),
    ("05/18/26", "TRADER JOES #740",          -47.90, "Groceries"),
    ("05/25/26", "COSTCO WHSE #1099",         -142.10,"Groceries"),
    ("05/07/26", "SHELL OIL 5744",            -41.10, "Gas & Convenience"),
    ("05/15/26", "CIRCLE K #2201",            -8.65,  "Gas & Convenience"),
    ("05/22/26", "EXXON MOBIL 4471",          -44.85, "Gas & Convenience"),
    ("05/08/26", "AMAZON.COM*A12BC7",         -37.99, "Shopping / Retail"),
    ("05/12/26", "TARGET 00021456",           -68.40, "Shopping / Retail"),
    ("05/16/26", "BEST BUY #481",             -129.99,"Shopping / Retail"),
    ("05/20/26", "AMAZON.COM*Z98YT2",         -24.50, "Shopping / Retail"),
    ("05/01/26", "NETFLIX.COM",               -15.49, "Software & Subs"),
    ("05/01/26", "SPOTIFY USA",               -11.99, "Software & Subs"),
    ("05/03/26", "ADOBE CREATIVE CLOUD",      -54.99, "Software & Subs"),
    ("05/10/26", "OPENAI CHATGPT SUBSCR",     -20.00, "Software & Subs"),
    ("05/15/26", "ICLOUD+ STORAGE 200GB",     -2.99,  "Software & Subs"),
    ("05/18/26", "AMAZON PRIME MEMBERSHIP",   -14.99, "Software & Subs"),
    ("05/05/26", "T-MOBILE POSTPAID",         -70.00, "Phone"),
    ("05/14/26", "USPS PO 3721",              -8.60,  "Shipping"),
    ("05/19/26", "UPS STORE #4410",           -14.25, "Shipping"),
]

# Money out but NOT everyday spending -- the app filters these out of "spending"
NON_SPEND_ROWS = [
    ("05/02/26", "WEALTHFRONT INVEST TRANSFER", -200.00, "Investing"),
    ("05/16/26", "ROBINHOOD DES:ACH",           -100.00, "Investing"),
    ("05/20/26", "ONLINE TRANSFER TO SAVINGS",  -300.00, "Transfers / Other"),
    ("05/28/26", "MONTHLY MAINTENANCE FEE",     -12.00,  "Fees"),
]

# Money in
INCOME = [
    ("05/01/26", "PAYROLL DES:DIRECT DEP",  2450.00, "Uncategorized"),
    ("05/15/26", "PAYROLL DES:DIRECT DEP",  2450.00, "Uncategorized"),
]

COLUMNS = ["Date", "Description", "Amount", "Section", "Category", "Type", "Source"]
_SOURCE = "eStmt_demo_2026-05.pdf"


def demo_dataframe() -> pd.DataFrame:
    """Build the full demo ledger as a DataFrame (Transactions schema)."""
    rows = []
    for date, desc, amt, cat in SPENDING:
        rows.append([date, desc, amt, "Spending", cat, "Spending", _SOURCE])
    for date, desc, amt, cat in NON_SPEND_ROWS:
        rows.append([date, desc, amt, "Other", cat, cat, _SOURCE])
    for date, desc, amt, cat in INCOME:
        rows.append([date, desc, amt, "Income", cat, "Income", _SOURCE])
    return pd.DataFrame(rows, columns=COLUMNS).sort_values("Date").reset_index(drop=True)

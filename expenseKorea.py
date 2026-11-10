import os
import sys
import webbrowser
from pathlib import Path
import pandas as pd

# 1. Determine traveler name from command-line argument (defaults to 'Aileen' if run directly in PyCharm)
if len(sys.argv) > 1:
    person1 = sys.argv[1].strip()
else:
    person1 = 'Aileen'

person2 = 'Michael'
krw_per_usd = 1350.0

# 2. Dynamically point to the CSV in the same directory as expenseKorea.py
base_dir = Path(__file__).resolve().parent
file_path = base_dir / 'South_Korea_Trip2026_Expense_Tracker.csv'

# 3. Read the CSV file
df = pd.read_csv(file_path)

# 4. Extract and rename the target columns (Unnamed: 4, 5, 6, and 16)
cols_to_use = ['Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 16']
subset = df[cols_to_use].copy()
subset.columns = ['Items', person1, 'expenses', person2]

# 5. Strip whitespace and filter rows matching person1 and valid entries for Michael
subset[person1] = subset[person1].astype(str).str.strip()
filtered = subset[
    (subset[person1].str.lower() == person1.lower()) &
    (subset[person2].notna())
].copy()

# 6. Helper function to clean currency formatting ($, ₩, commas, spaces)
def clean_currency(val):
    if pd.isna(val):
        return 0.0
    s = str(val).replace(',', '').replace('$', '').replace('₩', '').strip()
    try:
        return float(s)
    except ValueError:
        return 0.0

filtered['expenses_num'] = filtered['expenses'].apply(clean_currency)
filtered['person2_num'] = filtered[person2].apply(clean_currency)

# Skip rows where Michael's numeric share is 0 or invalid
filtered = filtered[filtered['person2_num'] != 0].copy()

# 7. Calculate totals in KRW and USD
total_expenses_krw = filtered['expenses_num'].sum()
total_person2_krw = filtered['person2_num'].sum()

total_expenses_usd = total_expenses_krw / krw_per_usd
total_person2_usd = total_person2_krw / krw_per_usd

# Format display columns to 2 decimal places
filtered['expenses'] = filtered['expenses_num'].map(lambda x: f"{x:,.2f}")
filtered[person2] = filtered['person2_num'].map(lambda x: f"{x:,.2f}")

# Keep only the 4 display columns
display_df = filtered[['Items', person1, 'expenses', person2]].copy()

# 8. Append Total (KRW) and Total (USD) summary rows at the bottom
total_rows = pd.DataFrame([
    {
        'Items': 'Total (KRW)',
        person1: '',
        'expenses': f"{total_expenses_krw:,.2f}",
        person2: f"{total_person2_krw:,.2f}"
    },
    {
        'Items': f'Total (USD @ {krw_per_usd:,.0f})',
        person1: '',
        'expenses': f"${total_expenses_usd:,.2f}",
        person2: f"${total_person2_usd:,.2f}"
    }
])

final_df = pd.concat([display_df, total_rows], ignore_index=True)

# 9. Build styled HTML report
html_table = final_df.to_html(index=False, classes='expense-table', border=0)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{person1} & {person2} - South Korea 2026 Expenses</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            margin: 30px;
            background-color: #f9fafb;
            color: #1f2937;
        }}
        h2 {{
            margin-bottom: 5px;
        }}
        .subtitle {{
            color: #6b7280;
            margin-bottom: 20px;
            font-size: 0.95rem;
        }}
        table.expense-table {{
            border-collapse: collapse;
            width: auto;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        table.expense-table th, table.expense-table td {{
            border: 1px solid #e5e7eb;
            padding: 8px 14px;
            white-space: nowrap;
        }}
        table.expense-table th {{
            background-color: #f3f4f6;
            font-weight: 600;
            text-align: left;
        }}
        /* Right-align numeric expense columns (columns 3 and 4) */
        table.expense-table td:nth-child(3),
        table.expense-table td:nth-child(4),
        table.expense-table th:nth-child(3),
        table.expense-table th:nth-child(4) {{
            text-align: right;
            font-variant-numeric: tabular-nums;
        }}
        /* Bold the bottom two total rows */
        table.expense-table tr:nth-last-child(1),
        table.expense-table tr:nth-last-child(2) {{
            font-weight: bold;
            background-color: #f9fafb;
        }}
        table.expense-table tr:nth-last-child(1) {{
            background-color: #eef2ff;
        }}
    </style>
</head>
<body>
    <h2>South Korea 2026 Expense Report: {person1} & {person2}</h2>
    <div class="subtitle">Exchange Rate: {krw_per_usd:,.0f} KRW = 1 USD</div>
    {html_table}
</body>
</html>
"""

# 10. Save the HTML file in the same directory as expenseKorea.py
output_file = base_dir / f"{person1}_{person2}.html"
output_file.write_text(html_content, encoding='utf-8')
print(f"Saved report: {output_file.name} | {person2} Total: {total_person2_krw:,.2f} KRW (${total_person2_usd:,.2f} USD)")

# Optional: Only auto-open in browser when run interactively without a batch flag
if os.environ.get("BATCH_RUN") != "1":
    webbrowser.open(f"file://{output_file}")
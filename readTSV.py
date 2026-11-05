import os
import webbrowser
import pandas as pd

# --- Configuration ---
people_names = ['Aileen', 'Michael']  # Add all travelers here
krw_per_usd = 1350.0

file_path = '/Users/michaellau/python2024/expenses/South_Korea_Trip2026_Expense_Tracker.tsv'
output_dir = '/Users/michaellau/python2024/expenses'

# Dynamically name the file based on person_name(s) (e.g., "Jocel.html" or "Jocel_Michael.html")
filename_base = "_".join(people_names)
output_html_path = os.path.join(output_dir, f'{filename_base}.html')

# Load the TSV file once
df = pd.read_csv(file_path, sep='\t')
cols = ['Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 16']

# Accumulators for the master report
person_sections_html = []
grand_total_krw = 0.0

# --- Loop through each person ---
for person_name in people_names:
    # 1. Filter dynamically by person name
    person_expenses = df[
        df['Unnamed: 5'].astype(str).str.strip().str.lower() == person_name.strip().lower()
        ].copy()

    # 2. Clean 'Unnamed: 16' and convert to numeric float
    person_expenses['Amount_Cleaned_16'] = (
        person_expenses['Unnamed: 16']
        .astype(str)
        .str.replace(r'[^\d.-]', '', regex=True)
    )
    person_expenses['Amount_Cleaned_16'] = pd.to_numeric(person_expenses['Amount_Cleaned_16'], errors='coerce')

    # 3. Filter OUT rows where Michael's amount is NaN or empty
    person_expenses = person_expenses[
        person_expenses['Amount_Cleaned_16'].notna() & (person_expenses['Amount_Cleaned_16'] > 0)
        ].copy()

    # Skip if no valid expenses are found for this person
    if person_expenses.empty:
        print(f"No valid expenses found for {person_name}. Skipping...")
        continue

    # 4. Calculate sums and conversions
    sum_unnamed_16 = person_expenses['Amount_Cleaned_16'].sum()
    total_usd = sum_unnamed_16 / krw_per_usd
    grand_total_krw += sum_unnamed_16

    # 5. Format display DataFrame with renamed columns
    rename_map = {
        'Unnamed: 4': 'Items',
        'Unnamed: 5': person_name,
        'Unnamed: 6': 'Expenses',
        'Unnamed: 16': 'Michael'
    }
    display_df = person_expenses[cols].rename(columns=rename_map).copy()

    # 6. Format numbers with comma separators and 2 decimal places
    display_df['Michael'] = person_expenses['Amount_Cleaned_16'].map('{:,.2f}'.format)

    # 7. Append a summary 'Total' row directly into the bottom of the table
    total_row = pd.DataFrame([{
        'Items': 'Total',
        person_name: '',
        'Expenses': '',
        'Michael': f"{sum_unnamed_16:,.2f}"
    }])
    display_df = pd.concat([display_df, total_row], ignore_index=True)

    # Generate HTML table for this person and append to our sections list
    table_html = display_df.to_html(classes='table', index=False)

    section_html = f"""
    <div class="person-section">
        <h2>{person_name}'s Expenses</h2>
        <div class="summary-card">
            <p><strong>Total KRW (Michael):</strong> &#8361;{sum_unnamed_16:,.2f}</p>
            <p><strong>Total USD:</strong> ${total_usd:,.2f} (Rate: {krw_per_usd:,.0f} KRW/USD)</p>
        </div>
        {table_html}
    </div>
    """
    person_sections_html.append(section_html)

# Calculate combined grand total in USD
grand_total_usd = grand_total_krw / krw_per_usd
all_sections_combined = "\n<hr class='divider'>\n".join(person_sections_html)

# --- Build Master HTML ---
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Expense Report - {filename_base}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 30px;
            color: #333;
        }}
        h1 {{ color: #1a252f; margin-bottom: 10px; }}
        h2 {{ color: #2c3e50; margin-top: 0; }}

        .grand-summary-card {{
            background: #eaf2f8;
            border-left: 5px solid #2980b9;
            padding: 15px 22px;
            margin-bottom: 30px;
            width: fit-content;
            border-radius: 4px;
        }}
        .grand-summary-card p {{ margin: 6px 0; font-size: 16px; }}

        .summary-card {{
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 12px 18px;
            margin-bottom: 15px;
            width: fit-content;
        }}
        .summary-card p {{ margin: 6px 0; font-size: 15px; }}

        .person-section {{
            margin-bottom: 35px;
        }}
        hr.divider {{
            border: 0;
            border-top: 1px solid #ccc;
            margin: 35px 0;
        }}

        /* Table Layout */
        table.table {{
            border-collapse: collapse;
            margin-top: 15px;
            width: auto;
        }}
        table.table th, table.table td {{
            border: 1px solid #ddd;
            padding: 8px 14px;
            text-align: left;
        }}

        /* Keep Items (col 1) and Person (col 2) close together */
        table.table th:nth-child(1), table.table td:nth-child(1) {{
            padding-right: 6px;
            white-space: nowrap;
        }}
        table.table th:nth-child(2), table.table td:nth-child(2) {{
            padding-left: 6px;
            padding-right: 18px;
            white-space: nowrap;
        }}

        /* Right-align amounts */
        table.table th:nth-child(3), table.table td:nth-child(3),
        table.table th:nth-child(4), table.table td:nth-child(4) {{
            text-align: right;
        }}

        table.table th {{
            background-color: #2c3e50;
            color: white;
        }}
        table.table tr:nth-child(even):not(:last-child) {{ background-color: #f2f2f2; }}

        /* Highlight Total Row at the bottom */
        table.table tr:last-child {{
            font-weight: bold;
            color: #ffffff;             /* White text for contrast */
            background-color: #007bff;  /* Bold blue background */
            border-top: 2px solid #0056b3;
        }}
    </style>
</head>
<body>
    <h1>South Korea Trip 2026 - Expense Report ({", ".join(people_names)})</h1>
    <div class="grand-summary-card">
       <p><strong>Combined Grand Total (Michael):</strong> ${(grand_total_krw / 1350.0):,.2f} USD</p>
        <p><strong>Combined Grand Total USD:</strong> ${grand_total_usd:,.2f} (Rate: {krw_per_usd:,.0f} KRW/USD)</p>
    </div>
    <hr class="divider">
    {all_sections_combined}
</body>
</html>
"""

with open(output_html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML report saved to: {output_html_path}")
webbrowser.open(f"file://{os.path.abspath(output_html_path)}")
#!/bin/bash
# Transferring Korea expense report
python3 -m venv .venv
source .venv/bin/activate
 for name in Aileen Jocel Jesse Mia; do
   echo "expense for $name"
   python3 expenseKorea.py "$name"
done

echo "Transferring Jesse, Mia, Aileen, and Jocel HTML files..."
scp Jesse_Michael.html Mia_Michael.html Aileen_Michael.html Jocel_Michael.html fastsnow@fastsnowboarder.com:~/public_html/koreaexpense

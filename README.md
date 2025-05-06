
# IRR/NPV/CBR Calculator (FastAPI backend)

Compare up to 6 alternatives based on CAPEX, OPEX, Benefits, Years, and Discount Rate.
Calculates NPV, IRR, and CB Ratio, and generates bar charts for each indicator.

## Deploy on Render
1. Upload files to GitHub
2. Create a new Web Service on render.com
3. Use:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`

Visit `/` to access the interface.

## Features
- Compare up to 6 alternatives
- Table of results (NPV, IRR, CB Ratio)
- Highlight best alternative by NPV
- Download Excel file with results
- Bar charts: NPV, IRR, CB Ratio

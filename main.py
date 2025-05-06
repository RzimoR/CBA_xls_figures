from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import numpy as np
import numpy_financial as npf
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def serve_index():
    return FileResponse("index.html")

class CBAInput(BaseModel):
    name: str
    capex: float
    opex: float
    benefits: float
    years: int
    rate: float

@app.post("/calculate")
def calculate(inputs: list[CBAInput]):
    results = []
    for item in inputs:
        try:
            rate_decimal = item.rate / 100.0
            df = pd.DataFrame({
                'Year': list(range(0, item.years + 1)),
                'CAPEX': [item.capex] + [0] * item.years,
                'OPEX': [0] + [item.opex] * item.years,
                'BENEFITS': [0] + [item.benefits] * item.years
            })
            df['discount_factor'] = 1 / (1 + rate_decimal) ** df['Year']
            df['discounted_capex'] = df['CAPEX'] * df['discount_factor']
            df['discounted_opex'] = df['OPEX'] * df['discount_factor']
            df['discounted_benefits'] = df['BENEFITS'] * df['discount_factor']
            df['NPV_year'] = df['discounted_benefits'] - (df['discounted_capex'] + df['discounted_opex'])
            df['NPV_cumulative'] = df['NPV_year'].cumsum()
            npv_cum = round(df['NPV_cumulative'].iloc[-1], 2)
            irr = round(npf.irr([-item.capex] + [item.benefits - item.opex] * item.years), 4)
            cbr = round(df['discounted_benefits'].sum() / (df['discounted_capex'].sum() + df['discounted_opex'].sum()), 4)
            results.append({
                "name": item.name,
                "capex": item.capex,
                "opex": item.opex,
                "benefits": item.benefits,
                "years": item.years,
                "rate": item.rate,
                "npv": npv_cum,
                "irr": irr,
                "cbr": cbr
            })
        except Exception as e:
            results.append({"name": item.name, "error": str(e)})
    return results
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import numpy as np
import numpy_financial as npf
import pandas as pd

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def get_index():
    return FileResponse("index.html")

class InputData(BaseModel):
    name: str
    capex: float
    opex: float
    benefits: float
    years: int
    rate: float

@app.post("/calculate")
def calculate(inputs: list[InputData]):
    results = []
    for item in inputs:
        try:
            r = item.rate / 100.0
            cashflows = [-item.capex] + [item.benefits - item.opex] * item.years
            irr = round(npf.irr(cashflows), 4)
            df = pd.DataFrame({
                "Year": list(range(item.years + 1)),
                "CAPEX": [item.capex] + [0] * item.years,
                "OPEX": [0] + [item.opex] * item.years,
                "BENEFITS": [0] + [item.benefits] * item.years
            })
            df["DF"] = 1 / (1 + r) ** df["Year"]
            df["Discounted_CAPEX"] = df["CAPEX"] * df["DF"]
            df["Discounted_OPEX"] = df["OPEX"] * df["DF"]
            df["Discounted_BENEFITS"] = df["BENEFITS"] * df["DF"]
            total_costs = df["Discounted_CAPEX"].sum() + df["Discounted_OPEX"].sum()
            total_benefits = df["Discounted_BENEFITS"].sum()
            npv = round(total_benefits - total_costs, 2)
            cbr = round(total_benefits / total_costs, 4)
            results.append({
                "name": item.name,
                "capex": item.capex,
                "opex": item.opex,
                "benefits": item.benefits,
                "years": item.years,
                "rate": item.rate,
                "npv": npv,
                "irr": irr,
                "cbr": cbr
            })
        except Exception as e:
            results.append({ "name": item.name, "error": str(e) })
    return results
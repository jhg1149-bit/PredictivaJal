from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from core.risk import Reading, calculate_risk, PROFILES
from core.storage import save_result, get_history
app=FastAPI(title="PredictivaJal API",version="2.0",description="API demostrativa para calcular un índice heurístico de condición de maquinaria")
class Telemetry(BaseModel):
    machine_id:str=Field(min_length=1,max_length=80)
    machine_type:Literal["inyectora","cnc"]
    temperature:float=Field(ge=0)
    vibration:float=Field(ge=0)
    current:float=Field(ge=0)
    hours:float=Field(ge=0)
@app.get("/health")
def health(): return {"status":"ok","service":"PredictivaJal API","version":"2.0"}
@app.get("/profiles")
def profiles(): return PROFILES
@app.post("/evaluate")
def evaluate(data:Telemetry):
    try:
        result=calculate_risk(Reading(**data.model_dump())); save_result(result); return result
    except ValueError as e: raise HTTPException(status_code=400,detail=str(e))
@app.get("/history")
def history(limit:int=100):
    if not 1<=limit<=1000: raise HTTPException(status_code=400,detail="limit debe estar entre 1 y 1000")
    return get_history(limit)

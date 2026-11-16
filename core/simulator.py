import random
from .risk import Reading, PROFILES

def generate_reading(machine_type="inyectora", scenario="mixed", machine_id="SIM-001"):
    p=PROFILES[machine_type]
    bands={"normal":(0.0,0.35),"warning":(0.45,0.72),"critical":(0.78,1.0),"mixed":(0.0,1.0)}
    lo,hi=bands[scenario]
    vals={}
    for key,lim in p["limits"].items():
        fraction=random.uniform(lo,hi)
        vals[key]=round(lim["nominal"]+fraction*(lim["critical"]-lim["nominal"]),2)
    return Reading(machine_id,machine_type,vals["temperature"],vals["vibration"],vals["current"],vals["hours"])

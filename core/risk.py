"""Motor de Índice de Riesgo de Falla (IRF) demostrativo.

IRF es un índice heurístico de condición, no una probabilidad de falla.
Los umbrales son configurables y no sustituyen las especificaciones del fabricante.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any

PROFILES: Dict[str, Dict[str, Any]] = {
    "inyectora": {"name":"Inyectora de plástico", "weights":{"temperature":0.35,"vibration":0.20,"current":0.30,"hours":0.15},
        "limits":{"temperature":{"nominal":65.0,"critical":95.0,"unit":"°C"},"vibration":{"nominal":1.5,"critical":4.5,"unit":"mm/s"},"current":{"nominal":12.0,"critical":25.0,"unit":"A"},"hours":{"nominal":100.0,"critical":500.0,"unit":"h"}}},
    "cnc": {"name":"Centro de maquinado CNC", "weights":{"temperature":0.25,"vibration":0.40,"current":0.25,"hours":0.10},
        "limits":{"temperature":{"nominal":65.0,"critical":95.0,"unit":"°C"},"vibration":{"nominal":1.5,"critical":4.5,"unit":"mm/s"},"current":{"nominal":12.0,"critical":25.0,"unit":"A"},"hours":{"nominal":100.0,"critical":500.0,"unit":"h"}}}
}

@dataclass
class Reading:
    machine_id: str
    machine_type: str
    temperature: float
    vibration: float
    current: float
    hours: float
    def validate(self):
        if not self.machine_id.strip(): raise ValueError("El identificador de máquina es obligatorio.")
        if self.machine_type not in PROFILES: raise ValueError("Tipo de máquina no reconocido.")
        for key in ("temperature","vibration","current","hours"):
            value=getattr(self,key)
            if isinstance(value,bool) or not isinstance(value,(int,float)) or value<0:
                raise ValueError(f"La variable {key} debe ser un número no negativo.")

def calculate_risk(reading: Reading) -> Dict[str, Any]:
    reading.validate(); profile=PROFILES[reading.machine_type]
    normalized={}; contributions={}
    for key,lim in profile["limits"].items():
        n=max(0.0,min(1.0,(getattr(reading,key)-lim["nominal"])/(lim["critical"]-lim["nominal"])))
        normalized[key]=round(n*100,2); contributions[key]=n*profile["weights"][key]
    score=round(sum(contributions.values())*100,2)
    if score<40: level="Normal"; recommendation="Mantener monitoreo y programa preventivo establecido."
    elif score<70: level="Advertencia"; recommendation="Programar inspección técnica y revisar la variable con mayor contribución."
    else: level="Crítico"; recommendation="Solicitar revisión de personal técnico calificado y seguir los protocolos de seguridad de la planta."
    dominant=max(contributions,key=contributions.get)
    return {"machine_id":reading.machine_id,"machine_type":reading.machine_type,"machine_name":profile["name"],"irf":score,"level":level,"recommendation":recommendation,"dominant_variable":dominant,"components":normalized,"weights":profile["weights"],"reading":asdict(reading),"model_note":"Índice heurístico demostrativo (0–100); no es una probabilidad estadística, no predice fecha de falla ni vida útil restante."}

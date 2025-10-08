from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="ComSys Project API", version="0.1.0")

class SampleDecision(BaseModel):
    wifi_rssi: float
    lte_rsrp: float
    nr_ssrsrp: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/decide")
def decide(x: SampleDecision):
    # dummy rule: chọn mạng có chỉ số lớn nhất (demo thôi)
    scores = {
        "WiFi": x.wifi_rssi,
        "4G": x.lte_rsrp,
        "5G": x.nr_ssrsrp,
    }
    best = max(scores, key=scores.get)
    return {"scores": scores, "selected": best}

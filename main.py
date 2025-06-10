from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from plot_example import generate_plot

app = FastAPI()

class PlotRequest(BaseModel):
    x: list[float]
    y: list[float]

@app.post("/plot")
def create_plot(data: PlotRequest):
    try:
        img_b64 = generate_plot(data.x, data.y)
        return {"image_base64": img_b64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

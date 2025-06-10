from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from plot_example import generate_plot

app = FastAPI()

class PlotRequest(BaseModel):
    x: list[str | float]
    y: list[float]
    chart_type: str = "line"
    title: str | None = None
    xlabel: str | None = None
    ylabel: str | None = None
    grid: bool = False
    return_format: str = "base64"  # base64 or png



@app.post("/plot")
def create_plot(data: PlotRequest):
    try:
        img_b64 = generate_plot(
            data.x,
            data.y,
            data.chart_type,
            data.title,
            data.xlabel,
            data.ylabel,
            data.grid
        )
        return {"image_base64": img_b64}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/help")
def get_help():
    return {
        "description": "This API generates base64-encoded images of graphs using Matplotlib.",
        "endpoint": "/plot",
        "method": "POST",
        "required_fields": ["x", "y"],
        "optional_fields": ["chart_type", "title", "xlabel", "ylabel", "grid"],
        "chart_types_supported": ["line", "bar", "scatter", "pie"],
        "example_payload": {
            "x": ["Q1", "Q2", "Q3"],
            "y": [120, 150, 180],
            "chart_type": "bar",
            "title": "Quarterly Sales",
            "xlabel": "Quarter",
            "ylabel": "Revenue",
            "grid": True
        }
    }

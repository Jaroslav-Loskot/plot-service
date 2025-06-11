from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from pydantic import BaseModel
from plot_example import generate_plot
from io import BytesIO
import secrets
from dotenv import load_dotenv
import os
from typing import Optional, Union
import base64

load_dotenv()

security = HTTPBasic()
USERNAME = os.getenv("PLT-SERVICE-USER", "admin")
PASSWORD = os.getenv("PLT-SERVICE-PSSWD", "secret123")

app = FastAPI()


from typing import Optional, Union

class PlotRequest(BaseModel):
    x: Optional[list[Union[str, float]]] = None
    y: Optional[Union[list[float], list[list[float]]]] = None  # Accepts 1D or 2D
    z: Optional[list[list[float]]] = None
    chart_type: str = "line"
    title: Optional[str] = None
    xlabel: Optional[str] = None
    ylabel: Optional[str] = None
    grid: bool = False
    return_format: str = "base64"
    description: Optional[str] = None
    series_labels: Optional[list[str]] = None  # New: labels for each line



def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})


@app.post("/plot")
def create_plot(data: PlotRequest, credentials: HTTPBasicCredentials = Depends(authenticate)):
    try:
        # Validate required fields
        if data.chart_type in ["line", "bar", "scatter", "pie"]:
            if data.x is None or data.y is None:
                raise ValueError(f"'{data.chart_type}' chart requires 'x' and 'y' fields.")
        elif data.chart_type == "heatmap":
            if data.z is None:
                raise ValueError("'heatmap' chart requires 'z' matrix data.")
        else:
            raise ValueError(f"Unsupported chart type: {data.chart_type}")

        image_bytes = generate_plot(
            x=data.x,
            y=data.y,
            z=data.z,
            chart_type=data.chart_type,
            title=data.title,
            xlabel=data.xlabel,
            ylabel=data.ylabel,
            grid=data.grid,
            series_labels=data.series_labels  # ✅ Add this line
        )

        if data.return_format == "png":
            return StreamingResponse(BytesIO(image_bytes), media_type="image/png")
        else:
            encoded = base64.b64encode(image_bytes).decode("utf-8")
            return {
                "image_base64": encoded,
                "description": data.description
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/help")
def get_help():
    return {
        "description": "This API generates graphs using Matplotlib. It supports base64-encoded images or raw PNG output.",
        "endpoint": "/plot",
        "method": "POST",
        "required_fields": ["chart_type"],
        "optional_fields": [
            "x",
            "y",
            "z",
            "series_labels",
            "title",
            "xlabel",
            "ylabel",
            "grid",
            "return_format",
            "description"
        ],
        "chart_types_supported": ["line", "bar", "scatter", "pie", "heatmap"],
        "notes": [
            "'y' can be a single list (1D) or multiple series (2D) for line charts.",
            "Each inner list in 2D 'y' must match the length of 'x'.",
            "'series_labels' is optional but useful for legends."
        ],
        "return_formats_supported": ["base64 (default)", "png"],
        "example_payloads": {
            "bar_chart": {
                "x": ["Q1", "Q2", "Q3"],
                "y": [120, 150, 180],
                "chart_type": "bar",
                "title": "Quarterly Sales",
                "xlabel": "Quarter",
                "ylabel": "Revenue",
                "grid": True,
                "return_format": "base64",
                "description": "Bar chart showing sales performance."
            },
            "multi_bar": {
                "chart_type": "bar",
                "x": ["Q1", "Q2", "Q3"],
                "y": [
                    [100, 120, 140],
                    [90, 110, 130]
                ],
                "series_labels": ["Product A", "Product B"],
                "title": "Quarterly Revenue Comparison",
                "xlabel": "Quarter",
                "ylabel": "Revenue",
                "grid": True,
                "return_format": "base64"
            },
            "multi_line": {
                "x": ["Jan", "Feb", "Mar"],
                "y": [
                    [10, 20, 30],
                    [15, 18, 25]
                ],
                "series_labels": ["Product A", "Product B"],
                "chart_type": "line",
                "title": "Monthly Sales Comparison",
                "xlabel": "Month",
                "ylabel": "Sales",
                "grid": True,
                "return_format": "base64"
            },
            "heatmap": {
                "chart_type": "heatmap",
                "z": [
                    [10, 20, 30],
                    [20, 25, 35],
                    [30, 35, 40]
                ],
                "title": "Matrix Heatmap",
                "xlabel": "Columns",
                "ylabel": "Rows",
                "return_format": "base64"
            }
        }
    }



@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}

@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(credentials: HTTPBasicCredentials = Depends(authenticate)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Plot Service Docs")


@app.get("/redoc", include_in_schema=False)
def custom_redoc_ui(credentials: HTTPBasicCredentials = Depends(authenticate)):
    return get_redoc_html(openapi_url="/openapi.json", title="Plot Service ReDoc")

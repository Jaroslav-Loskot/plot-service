from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from plot_example import generate_plot
from fastapi.responses import StreamingResponse
from io import BytesIO
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends
import secrets
from dotenv import load_dotenv
import os

load_dotenv()

security = HTTPBasic()
USERNAME = os.getenv("USERNAME", "admin")
PASSWORD = os.getenv("PASSWORD", "secret123")

app = FastAPI()

class PlotRequest(BaseModel):
    x: list[str | float]
    y: list[float]
    chart_type: str = "line"
    title: str | None = None
    xlabel: str | None = None
    ylabel: str | None = None
    grid: bool = False
    return_format: str = "base64"
    description: str | None = None

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})



@app.post("/plot")
def create_plot(
    data: PlotRequest,
    credentials: HTTPBasicCredentials = Depends(authenticate)  # 👈 Auth here
):
    try:
        image_bytes = generate_plot(
            data.x,
            data.y,
            data.chart_type,
            data.title,
            data.xlabel,
            data.ylabel,
            data.grid
        )

        if data.return_format == "png":
            return StreamingResponse(BytesIO(image_bytes), media_type="image/png")
        else:
            import base64
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
        "description": "This API generates graphs using Matplotlib. It supports both base64-encoded images and raw PNG responses.",
        "endpoint": "/plot",
        "method": "POST",
        "required_fields": ["x", "y"],
        "optional_fields": [
            "chart_type",
            "title",
            "xlabel",
            "ylabel",
            "grid",
            "return_format",
            "description"
        ],
        "chart_types_supported": ["line", "bar", "scatter", "pie"],
        "return_formats_supported": ["base64 (default)", "png"],
        "notes": [
            "PNG responses return only the image and exclude description or other metadata.",
            "Base64 format includes the encoded image and may include optional fields like description."
        ],
        "example_payload": {
            "x": ["Q1", "Q2", "Q3"],
            "y": [120, 150, 180],
            "chart_type": "bar",
            "title": "Quarterly Sales",
            "xlabel": "Quarter",
            "ylabel": "Revenue",
            "grid": True,
            "return_format": "base64",
            "description": "Bar chart showing sales over Q1 to Q3."
        }
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    return {"status": "ready"}


from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(credentials: HTTPBasicCredentials = Depends(authenticate)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Plot Service Docs")

@app.get("/redoc", include_in_schema=False)
def custom_redoc_ui(credentials: HTTPBasicCredentials = Depends(authenticate)):
    return get_redoc_html(openapi_url="/openapi.json", title="Plot Service ReDoc")

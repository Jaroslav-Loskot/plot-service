from pathlib import Path
import uuid
import threading
import time
import secrets
import base64
import os
from io import BytesIO
from typing import Optional, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from pydantic import BaseModel
from dotenv import load_dotenv

from plot_example import generate_plot  # Custom plot logic

# Load environment variables
load_dotenv()

# Temporary file storage for plot images
TEMP_DIR = Path("temp_images")
TEMP_DIR.mkdir(exist_ok=True)

# Basic Auth setup
security = HTTPBasic()
USERNAME = os.getenv("PLT-SERVICE-USER", "admin")
PASSWORD = os.getenv("PLT-SERVICE-PSSWD", "secret123")

# Lifespan event to clean old files on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_old_files(TEMP_DIR, max_age_seconds=300)
    yield

app = FastAPI(lifespan=lifespan)

# Request body for plot creation
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
    series_labels: Optional[list[str]] = None

# Basic HTTP auth verification
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

# Schedule auto-delete of temporary image file
def auto_delete(filepath: Path, delay_seconds: int = 300):
    def delete():
        time.sleep(delay_seconds)
        try:
            filepath.unlink()
        except FileNotFoundError:
            pass
    threading.Thread(target=delete, daemon=True).start()

# Remove expired temporary image files
def cleanup_old_files(directory: Path, max_age_seconds: int = 300):
    print(f"[Startup Cleanup] Checked temp files in {directory}")
    now = time.time()
    for file in directory.glob("*.png"):
        try:
            if file.stat().st_mtime < (now - max_age_seconds):
                file.unlink()
        except Exception as e:
            print(f"Error deleting {file.name}: {e}")

# Main endpoint to create and return plot in various formats
@app.post("/plot")
def create_plot(data: PlotRequest, credentials: HTTPBasicCredentials = Depends(authenticate)):
    try:
        # Validate required fields for each chart type
        if data.chart_type in ["line", "bar", "scatter"]:
            if data.x is None or data.y is None:
                raise ValueError(f"'{data.chart_type}' chart requires both 'x' and 'y' fields.")
        elif data.chart_type == "pie":
            if data.y is None:
                raise ValueError("'pie' chart requires 'y' values.")
        elif data.chart_type == "heatmap":
            if data.z is None:
                raise ValueError("'heatmap' chart requires 'z' matrix data.")
        else:
            raise ValueError(f"Unsupported chart type: {data.chart_type}")

        # Generate image bytes
        image_bytes = generate_plot(
            x=data.x,
            y=data.y,
            z=data.z,
            chart_type=data.chart_type,
            title=data.title,
            xlabel=data.xlabel,
            ylabel=data.ylabel,
            grid=data.grid,
            series_labels=data.series_labels
        )

        # Return based on format
        if data.return_format == "png":
            return StreamingResponse(BytesIO(image_bytes), media_type="image/png")

        elif data.return_format == "url":
            filename = f"{uuid.uuid4()}.png"
            filepath = TEMP_DIR / filename
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            auto_delete(filepath)
            return {
                "url": f"/download/{filename}",
                "format": "url",
                "description": data.description or "Temporary chart URL (expires in ~5 min)"
            }

        else:
            encoded = base64.b64encode(image_bytes).decode("utf-8")
            return {
                "image_base64": encoded,
                "description": data.description
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Serve temporary PNG images
@app.get("/download/{filename}")
def download_plot(filename: str):
    filepath = TEMP_DIR / filename
    if filepath.exists():
        return FileResponse(filepath, media_type="image/png", filename=filename)
    raise HTTPException(status_code=404, detail="File not found or expired.")

# Help endpoint describing usage and payload examples
@app.get("/help")
def get_help():
    return {
        "description": "This API generates graphs using Matplotlib. It supports base64-encoded images, raw PNG output, or a temporary URL to the image.",
        "endpoint": "/plot",
        "method": "POST",
        "required_fields": ["chart_type"],
        "optional_fields": [
            "x", "y", "z", "series_labels", "title", "xlabel", "ylabel", "grid", "return_format", "description"
        ],
        "chart_types_supported": ["line", "bar", "scatter", "pie", "heatmap"],
        "return_formats_supported": [
            "base64 (default) – returns base64-encoded PNG string in JSON",
            "png – returns raw image stream with 'image/png' content type",
            "url – returns a temporary download URL (expires in ~5 minutes)"
        ],
        "notes": [
            "'y' can be a single list (1D) or multiple series (2D) for line and bar charts.",
            "Each inner list in 2D 'y' must match the length of 'x'.",
            "'series_labels' is optional but used for labeling pie slices and legends in multi-series charts.",
            "Use 'url' return_format for browser or client-side rendering via temporary links."
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    return {"status": "ready"}

# Protect interactive docs with basic auth
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(credentials: HTTPBasicCredentials = Depends(authenticate)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Plot Service Docs")

@app.get("/redoc", include_in_schema=False)
def custom_redoc_ui(credentials: HTTPBasicCredentials = Depends(authenticate)):
    return get_redoc_html(openapi_url="/openapi.json", title="Plot Service ReDoc")
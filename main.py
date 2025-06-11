from pathlib import Path
import uuid
import threading
from contextlib import asynccontextmanager
import time
from fastapi.responses import FileResponse
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

TEMP_DIR = Path("temp_images")
TEMP_DIR.mkdir(exist_ok=True)

security = HTTPBasic()
USERNAME = os.getenv("PLT-SERVICE-USER", "admin")
PASSWORD = os.getenv("PLT-SERVICE-PSSWD", "secret123")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ Cleanup old files on startup
    cleanup_old_files(TEMP_DIR, max_age_seconds=300)
    yield
    # You can do more cleanup on shutdown here if needed

app = FastAPI(lifespan=lifespan)


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

def auto_delete(filepath: Path, delay_seconds: int = 300):
    def delete():
        time.sleep(delay_seconds)
        try:
            filepath.unlink()
        except FileNotFoundError:
            pass
    threading.Thread(target=delete, daemon=True).start()


def cleanup_old_files(directory: Path, max_age_seconds: int = 300):
    print(f"[Startup Cleanup] Checked temp files in {directory}")
    now = time.time()
    for file in directory.glob("*.png"):
        try:
            if file.stat().st_mtime < (now - max_age_seconds):
                file.unlink()
        except Exception as e:
            print(f"Error deleting {file.name}: {e}")



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
        elif data.return_format == "url":
            filename = f"{uuid.uuid4()}.png"
            filepath = TEMP_DIR / filename
            with open(filepath, "wb") as f:
                f.write(image_bytes)

            auto_delete(filepath)  # Auto-delete after timeout

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


@app.get("/download/{filename}")
def download_plot(filename: str):
    filepath = TEMP_DIR / filename
    if filepath.exists():
        return FileResponse(filepath, media_type="image/png", filename=filename)
    raise HTTPException(status_code=404, detail="File not found or expired.")


@app.get("/help")
def get_help():
    return {
        "description": "This API generates graphs using Matplotlib. It supports base64-encoded images, raw PNG output, or a temporary URL to the image.",
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
        "return_formats_supported": [
            "base64 (default) – returns base64-encoded PNG string in JSON",
            "png – returns raw image stream with 'image/png' content type",
            "url – returns a temporary download URL (expires in ~5 minutes)"
        ],
        "notes": [
            "'y' can be a single list (1D) or multiple series (2D) for line and bar charts.",
            "Each inner list in 2D 'y' must match the length of 'x'.",
            "'series_labels' is optional but useful for legends.",
            "Use 'url' return_format for browser or client-side rendering via temporary links."
        ],
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
            },
            "url_format_example": {
                "x": ["Jan", "Feb", "Mar"],
                "y": [10, 20, 30],
                "chart_type": "line",
                "title": "Chart with Temporary URL",
                "return_format": "url",
                "description": "Returns a link to a temp-hosted PNG (valid ~5 min)."
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

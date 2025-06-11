
# 🧮 Plot Service API

A lightweight, self-hosted **FastAPI** microservice for generating graphs — including **line**, **bar**, **scatter**, **pie**, and **heatmap** — using **Matplotlib**.

Designed to power **AI Agents** (like in **n8n**), automation flows, or scripting tools. Outputs base64-encoded images, raw PNG streams, or temporary URLs.

---

## 🚀 Features

- 📊 Supports: `line`, `bar`, `scatter`, `pie`, and `heatmap`
- 📦 Returns graphs as **base64**, raw **PNG**, or **temporary URL**
- ⚙️ Customizable: title, axis labels, grid, etc.
- 🔐 HTTP Basic Auth via `.env`
- 🤖 LLM-/Agent-friendly `/help` endpoint (structured for parsing)
- 🐳 Dockerized with **non-root**, Python 3.12 base
- 🧰 Optional `Makefile` for easy dev shortcuts

---

## 🧪 Example Requests

### 📊 Bar Chart

```

http
POST /plot
Content-Type: application/json

{
"chart\_type": "bar",
"x": \["Q1", "Q2", "Q3"],
"y": \[
\[100, 120, 140],
\[90, 110, 130]
],
"series\_labels": \["Product A", "Product B"],
"title": "Quarterly Revenue Comparison",
"xlabel": "Quarter",
"ylabel": "Revenue",
"grid": true,
"return\_format": "base64"
}

```

### 📈 Multi-Line Comparison

```

http
POST /plot
Content-Type: application/json
Authorization: Basic <base64-credentials>

{
"chart\_type": "line",
"x": \["Jan", "Feb", "Mar"],
"y": \[
\[10, 20, 30],
\[15, 18, 25]
],
"series\_labels": \["Product A", "Product B"],
"title": "Monthly Sales Comparison",
"xlabel": "Month",
"ylabel": "Units Sold",
"grid": true,
"return\_format": "base64"
}

```

### 🔥 Heatmap

```

http
POST /plot
Content-Type: application/json
Authorization: Basic <base64-credentials>

{
"chart\_type": "heatmap",
"z": \[
\[10, 20, 30],
\[20, 25, 35],
\[30, 35, 40]
],
"title": "Matrix Heatmap",
"xlabel": "Columns",
"ylabel": "Rows",
"return\_format": "base64",
"description": "This heatmap represents intensity values in a 3x3 matrix."
}

```

> ✅ Note: `x` and `y` are not required for heatmap.  
> ✅ Be sure to pass the correct `Authorization` header using base64-encoded `username:password`.

---

### 📤 Return Format: URL

You can also set `"return_format": "url"` to receive a temporary link to download the image.

```

http
POST /plot
Content-Type: application/json
Authorization: Basic <base64-credentials>

{
"chart\_type": "line",
"x": \["Jan", "Feb", "Mar"],
"y": \[100, 120, 90],
"title": "Monthly Visitors",
"xlabel": "Month",
"ylabel": "Count",
"grid": true,
"return\_format": "url",
"description": "Line chart showing monthly visitors"
}

```

Example Response:

```

{
"url": "/download/1718112245\_402ab4e3-38e2-4e33-9a2d-16a03d9e3c0a.png",
"format": "url",
"description": "Line chart showing monthly visitors"
}

````

> 🧹 Temporary files are auto-deleted after ~5 minutes.

---

## 🔐 Authentication

This service uses **HTTP Basic Auth**.

### Set credentials in `.env`:

```env
USERNAME=your-username
PASSWORD=your-strong-password
````

Pass encoded credentials in the header:

```
Authorization: Basic <base64(username:password)>
```

---

## 📦 Usage with Docker

### 🔨 Build & Run

```bash
docker build -t plot-service .
docker run -p 8000:8000 plot-service
```

### Or use Docker Compose

```bash
docker compose up --build
```

---

## 🔧 API Endpoints

| Method | Path      | Description                            |
| ------ | --------- | -------------------------------------- |
| POST   | `/plot`   | Generate a graph (base64, PNG, or URL) |
| GET    | `/help`   | LLM-friendly structured usage info     |
| GET    | `/health` | Health check                           |
| GET    | `/ready`  | Readiness probe                        |
| GET    | `/docs`   | Swagger UI (HTTP auth protected)       |
| GET    | `/redoc`  | ReDoc UI (HTTP auth protected)         |

---

## ⚙️ Makefile Shortcuts

If you're using the included `Makefile`, try:

```bash
make build         # Build Docker image
make run           # Run container
make test-help     # Curl the /help endpoint
make stop          # Stop the container
```

---

## 📁 Project Structure

```
.
├── main.py              # FastAPI entrypoint
├── plot_example.py      # Plotting logic (matplotlib)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Local dev runner
├── Makefile             # Dev convenience commands
├── .env                 # Credentials for auth (not committed)
└── README.md            # You're here
```

---

## 👤 Author

Created by [Jaroslav Loskot](https://github.com/Jaroslav-Loskot)
Licensed under the [MIT License](LICENSE)
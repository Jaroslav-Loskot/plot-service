# 🧮 Plot Service API

A lightweight, self-hosted **FastAPI** microservice for generating graphs — including **line**, **bar**, **scatter**, **pie**, and **heatmap** — using **Matplotlib**.

Designed to power **AI Agents** (like in **n8n**), automation flows, or scripting tools. Outputs base64-encoded images or raw PNG streams.

---

## 🚀 Features

- 📊 Supports: `line`, `bar`, `scatter`, `pie`, and `heatmap`
- 📦 Returns graphs as **base64** or raw **PNG**
- ⚙️ Customizable: title, axis labels, grid, etc.
- 🔐 HTTP Basic Auth via `.env`
- 🤖 LLM-/Agent-friendly `/help` endpoint (structured for parsing)
- 🐳 Dockerized with **non-root**, Python 3.12 base
- 🧰 Optional `Makefile` for easy dev shortcuts

---

Absolutely! Here's the updated `README.md` with **two complete example requests** under the "🧪 Example Requests" section — one standard (bar chart), one heatmap.


## 🧪 Example Requests

### 📊 Bar Chart

```http
POST /plot
Content-Type: application/json
Authorization: Basic <base64-credentials>

{
  "x": ["Q1", "Q2", "Q3"],
  "y": [120, 150, 180],
  "chart_type": "bar",
  "title": "Quarterly Sales",
  "xlabel": "Quarter",
  "ylabel": "Revenue",
  "grid": true,
  "return_format": "base64",
  "description": "Bar chart showing sales performance over three quarters."
}
````

---

### 🔥 Heatmap

```http
POST /plot
Content-Type: application/json
Authorization: Basic <base64-credentials>

{
  "chart_type": "heatmap",
  "z": [
    [10, 20, 30],
    [20, 25, 35],
    [30, 35, 40]
  ],
  "title": "Matrix Heatmap",
  "xlabel": "Columns",
  "ylabel": "Rows",
  "return_format": "base64",
  "description": "This heatmap represents intensity values in a 3x3 matrix."
}
```

> ✅ Note: `x` and `y` are not required for heatmap.
> ✅ Be sure to pass the correct `Authorization` header using base64-encoded `username:password`.


---

## 🔐 Authentication

This service uses **HTTP Basic Auth**.

### Set credentials in `.env`:

```env
USERNAME=your-username
PASSWORD=your-strong-password
```

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

| Method | Path      | Description                        |
| ------ | --------- | ---------------------------------- |
| POST   | `/plot`   | Generate a graph (base64 or PNG)   |
| GET    | `/help`   | LLM-friendly structured usage info |
| GET    | `/health` | Health check                       |
| GET    | `/ready`  | Readiness probe                    |
| GET    | `/docs`   | Swagger UI (HTTP auth protected)   |
| GET    | `/redoc`  | ReDoc UI (HTTP auth protected)     |

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
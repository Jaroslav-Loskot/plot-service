# 🧮 Plot Service API

A lightweight, self-hosted FastAPI microservice for generating graphs (line, bar, scatter, pie) using Matplotlib.

This is designed for use with **AI Agents** (like in n8n), scripting, or other automation tools. Supports base64 image output or raw PNG stream.

---

## 🚀 Features

- Supports **line**, **bar**, **scatter**, and **pie** charts
- Returns graphs as **base64** or raw **PNG**
- Customizable: title, labels, grid, and more
- Built with **FastAPI**, **Matplotlib**, and **Docker**
- **n8n AI Agent** friendly via `/help` endpoint
- Lightweight, non-root Docker image (Python 3.12)

---

## 🧪 Example Request

```http
POST /plot
Content-Type: application/json

{
  "x": ["Q1", "Q2", "Q3"],
  "y": [120, 150, 180],
  "chart_type": "bar",
  "title": "Quarterly Sales",
  "xlabel": "Quarter",
  "ylabel": "Revenue",
  "grid": true,
  "return_format": "base64",
  "description": "Sales performance over three quarters"
}
````

---

## 📦 Usage with Docker

### Build and run:

```bash
docker build -t plot-service .
docker run -p 8000:8000 plot-service
```

### Or using Docker Compose:

```bash
docker compose up --build
```

---

## 🧰 Endpoints

| Method | Path      | Description                        |
| ------ | --------- | ---------------------------------- |
| POST   | `/plot`   | Generate a graph                   |
| GET    | `/help`   | Discover usage (for LLMs + humans) |
| GET    | `/health` | Health check                       |
| GET    | `/ready`  | Ready check                        |

---

## ⚙️ Makefile Shortcuts

If using the included `Makefile`:

```bash
make build         # Build Docker image
make run           # Run container
make test-help     # Test /help endpoint
make stop          # Stop container
```

---

## 🔒 Security (Optional)

You can add API keys, rate limiting, or basic auth if deploying publicly.

---

## 📁 Project Structure

```
.
├── main.py              # FastAPI entrypoint
├── plot_example.py      # Plotting logic
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container definition
├── docker-compose.yml   # Local dev runner
├── Makefile             # Dev commands (optional)
└── README.md            # This file
```

---

## 👤 Author

Created by [Jaroslav Loskot](https://github.com/Jaroslav-Loskot)
MIT License

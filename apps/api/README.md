# Product Pipeline API

FastAPI backend for executing the product pipeline.

## Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
# Development mode
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Endpoints

### Health
- `GET /api/health` - Health check

### Pipeline Execution
- `POST /api/pipeline/execute` - Execute a pipeline step (BRD, Design, or Tickets)
- `GET /api/pipeline/status/{task_id}` - Get execution status
- `GET /api/pipeline/tasks` - List all tasks

## Architecture

```
app/
├── __init__.py
├── main.py              # FastAPI app
├── api/
│   └── routes/
│       ├── health.py    # Health endpoints
│       └── pipeline.py  # Pipeline endpoints
├── core/                # Core utilities
└── services/            # Business logic
```

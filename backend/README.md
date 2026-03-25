# Backend (FastAPI)

DRDO Command Dashboard backend with:

- `POST /alert`
- `GET /alerts`
- `GET /logs`
- `WebSocket /ws`
- In-memory + SQLite persistence

## Run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

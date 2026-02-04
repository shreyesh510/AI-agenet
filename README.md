# AI Agent Projects
  cd D:\strakly\strakly-bot
  python -m venv venv
  venv\Scripts\activate
  pip install -r requirements.txt
## Projects

### 1. main-agent (FastAPI)

```bash
cd main-agent
venv\Scripts\activate
uvicorn main:app --reload
```

Runs on: http://localhost:8000

### 2. parcel-backend (Express + PostgreSQL)

```bash
cd parcel-backend
npm install
npm start
```

Runs on: http://localhost:3000

**Note:** Update `.env` file with your PostgreSQL credentials before starting.

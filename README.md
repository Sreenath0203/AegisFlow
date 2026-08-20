# AegisFlow – Supply Chain Decision Intelligence Platform

AegisFlow is an AI-Powered Autonomous Supply Chain Decision Intelligence Platform that detects supply-chain risks, analyzes root causes, predicts operational impacts, compares recovery strategies, and provides explainable AI recommendations.

---

## Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript (No React, Angular, or Vue)
- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Database**: PostgreSQL (with automatic SQLite local fallback for development)
- **IBM AI Integration**: Designed for IBM watsonx.ai, IBM Granite, IBM watsonx.ai RAG, and IBM Data Prep Kit.

---

## Project Structure

```
AegisFlow/
├── frontend/             # HTML5 + CSS3 + Vanilla JS Dashboard
│   ├── index.html
│   ├── css/
│   ├── js/
│   ├── pages/
│   └── assets/
│
├── backend/              # Python FastAPI Application
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── database/
│   └── config/
│
├── ai-services/          # IBM AI Service Integration Layer
│   ├── agents/           # News, Supplier Risk, Compliance & Decision Agents
│   ├── granite/          # IBM Granite watsonx.ai integration interface
│   ├── rag/              # IBM watsonx.ai RAG retrieval interface
│   └── services/         # Agent orchestration services
│
├── data-pipeline/        # Data Prep Kit & Ingestion Structure
│   ├── ingestion/
│   ├── processing/
│   ├── transformation/
│   └── datasets/
│
├── database/             # PostgreSQL DDL & migrations
├── tests/                # Automated test suite
├── docs/                 # Documentation
├── deployment/           # Docker configuration
├── .gitignore
└── README.md
```

---

## Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Backend Server
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Verify backend in browser:
- Root: `http://127.0.0.1:8000`
- Health: `http://127.0.0.1:8000/health`
- Swagger Docs: `http://127.0.0.1:8000/docs`

### 3. Open Frontend
Open `frontend/index.html` directly in a browser or access `http://127.0.0.1:8000` via FastAPI static server.

---

## IBM AI Integrations Configuration
IBM AI services (watsonx.ai, IBM Granite, RAG, Data Prep Kit) are configured using environment variables in `.env` (e.g. `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL`, `MODEL_ID`). Services are cleanly interfaced and ready for credentials configuration.

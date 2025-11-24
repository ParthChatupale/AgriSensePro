# KrushiRakshak Backend

This is the backend part of the KrushiRakshak project. It’s made using FastAPI, and it basically handles all the stuff the frontend depends on — user accounts, agri-data processing, Fusion Engine logic, the farmer community routes, and the Gemini chatbot. (If you’re trying to see how everything ties together, the Fusion Engine docs are a good starting point.)

## What This Backend Does

- **User Management** – signup, login, profile updates (secured via JWT).
- **Fusion Engine** – processes weather, NDVI, market, etc., to craft crop advisories.
- **Community Features** – posts, likes, comments live here.
- **AI Chatbot** – calls Google Gemini for question/answer flow.
- **Data Services** – pulls from IMD, Agmarknet, Bhuvan, then normalizes it.

## Quick Start

### Install Dependencies
Start by creating a virtual environment and installing everything from `requirements.txt`.

```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

```bash
# Linux / macOS
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Set Up Environment Variables
Inside `backend/`, create `.env` (copy `.env.example` if it exists) and add:
```
SECRET_KEY=your-secret-key-here-make-it-long-and-random
DATABASE_URL=sqlite:///./agrisense_dev.db
GEMINI_API_KEY=your-google-gemini-api-key-optional
```
- `SECRET_KEY` → used for JWT, so keep it long/random.
- SQLite works great for dev/testing (default). For Postgres use `postgresql://user:password@localhost/agrisense_db`.
- Gemini API key only needed if you plan to hit the chatbot endpoint.

### Run the Server
```bash
uvicorn app.main:app --reload --port 8000
```
Backend sits at <http://127.0.0.1:8000>.

### API Docs
- Swagger UI → <http://127.0.0.1:8000/docs>  
- ReDoc → <http://127.0.0.1:8000/redoc>  
You can test endpoints directly from those pages.

## Project Structure

```
backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── auth.py
│   ├── fusion_engine.py
│   ├── community.py
│   ├── ai.py
│   ├── services/
│   │   ├── weather.py
│   │   ├── market.py
│   │   ├── ndvi.py
│   │   └── crop_stage.py
│   └── utils/
├── data/
│   ├── weather_data.json
│   ├── market_prices.json
│   ├── crop_health.json
│   └── crops_metadata.json
├── rules/
│   ├── pest_rules.json
│   ├── irrigation_rules.json
│   └── market_rules.json
├── etl/
│   └── make_features.py
├── test_scripts/
│   └── README.md
├── migrations/
├── requirements.txt
└── README.md
```

## Main Components

- **Authentication (`app/auth.py`)**  
  Routes: `POST /api/auth/signup`, `POST /api/auth/login`, `GET /api/auth/me`, `PATCH /api/auth/profile`

- **Fusion Engine (`app/fusion_engine.py`)**  
  Handles `/fusion/dashboard` and `/fusion/advisory/{crop}` using rules + incoming sensor data.

- **Community (`app/community.py`)**  
  Endpoints for posts, creating posts, likes, comments.

- **AI Chatbot (`app/ai.py`)**  
  `POST /ai/chat` (Gemini)

## Database

- Default DB: `SQLite (agrisense_dev.db)` – good enough for dev.  
- Production: point `DATABASE_URL` to Postgres (`postgresql://username:password@localhost/agrisense_db`).  
- On first run, tables are auto-created (the initialization happens inside `app/main.py`).


## Testing

Use the scripts under `test_scripts/`:
```bash
python test_scripts/test_dashboard.py
python test_scripts/test_advisory.py cotton
python test_scripts/test_all.py
```
Refer to `test_scripts/README.md` for expected responses.

## API Endpoints Summary

- **Public**: `GET /`, `GET /fusion/health`
- **Requires JWT**: include `Authorization: Bearer <token>` (get the token via `/api/auth/login`)

## Troubleshooting

- **Module not found**: run commands from `backend/`, activate your venv, reinstall deps.  
- **Database errors**: check file permissions (SQLite) or connection string (Postgres); tables auto-create.  
- **Port already in use**: `uvicorn app.main:app --reload --port 8001`  
- **CORS issues**: default allows `http://localhost:8080`. Update `main.py` if frontend origin differs.

## More Information

- Fusion Engine setup → `FUSION_ENGINE_SETUP.md`
- Testing guide → `test_scripts/README.md`
- Migration notes → `migrations/README_MIGRATION.md`
- Full docs → `../docs/Agrisense_Documentation.md`

## Notes

- Designed to work smoothly with the React frontend.
- All responses are JSON, errors follow a consistent format.
- Fusion Engine rules live in `backend/rules/*.json`.
- External API integrations are handled via `app/services/`.
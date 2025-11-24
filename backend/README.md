KrushiRakshak Backend

Last updated: Nov 2025 — Maintainer: Parth Chatupale

This is the backend server for KrushiRakshak, built with FastAPI. It manages user authentication, agricultural data processing, the Fusion Engine, and the community section. Most of this grew gradually as the project expanded, so a few modules reflect that evolution.

What This Backend Does

User Management: Sign up, login, and profile updates using secure JWT authentication

Fusion Engine: Combines weather, market and satellite inputs to generate crop advisories

Community Features: Supports posts, comments and likes for the farmer community

AI Chatbot: Integrated with Google Gemini for farming-related queries

Data Services: Fetches and processes live/periodic data from IMD, Agmarknet, and Bhuvan APIs

(I personally recommend checking the Fusion Engine section first if you're curious how advisories are formed.)

Quick Start
1. Install Dependencies

First, create a virtual environment and install the required packages.
I usually do this on a fresh environment to avoid dependency conflicts.

Windows (PowerShell)

python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt


Linux / Mac

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2. Set Up Environment Variables

Create a .env file inside the backend/ folder (you can copy from .env.example if it exists):

SECRET_KEY=your-secret-key-here-make-it-long-and-random
DATABASE_URL=sqlite:///./agrisense_dev.db
GEMINI_API_KEY=your-google-gemini-api-key-optional


Notes from experience:

SECRET_KEY must be long—avoid short keys, they cause token issues.

SQLite works perfectly for local dev.

For PostgreSQL: postgresql://user:password@localhost/agrisense_db

GEMINI_API_KEY is optional unless you want chatbot responses.

3. Run the Server
uvicorn app.main:app --reload --port 8000


The API should be live at:
👉 http://127.0.0.1:8000

4. API Documentation

You can check the auto-generated API docs:

Swagger UI → http://127.0.0.1:8000/docs

ReDoc → http://127.0.0.1:8000/redoc

(I end up using Swagger more for quick testing.)

Project Structure
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database connection and session setup
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic models
│   ├── crud.py              # Helper DB operations
│   ├── auth.py              # Signup, login, profile
│   ├── fusion_engine.py     # Dashboard & advisory
│   ├── community.py         # Posts, comments, likes
│   ├── ai.py                # AI chatbot integration
│   ├── services/
│   │   ├── weather.py       # IMD weather fetcher
│   │   ├── market.py        # Agmarknet market prices
│   │   ├── ndvi.py          # Bhuvan NDVI processing
│   │   └── crop_stage.py    # Crop stage detection
│   └── utils/               # Helpers
├── data/                    # Mock JSON data
├── rules/                   # Fusion Engine rules
├── etl/                     # Feature extraction scripts
├── test_scripts/            # Testing helpers
├── migrations/
├── requirements.txt
└── README.md

Main Components
Authentication (app/auth.py)

Handles:

POST /api/auth/signup

POST /api/auth/login

GET /api/auth/me

PATCH /api/auth/profile

Fusion Engine (app/fusion_engine.py)

GET /fusion/dashboard

GET /fusion/advisory/{crop}

(The advisory logic depends on a rule set + incoming sensor data.)

Community (app/community.py)

GET /api/community/posts

POST /api/community/posts

POST /api/community/posts/{post_id}/like

POST /api/community/posts/{post_id}/comment

AI Chatbot (app/ai.py)

POST /ai/chat

Database

Default DB: SQLite (agrisense_dev.db).
Works well for development and testing.

For production:

DATABASE_URL=postgresql://username:password@localhost/agrisense_db


Tables are auto-created when you run the server for the first time.

Testing

We have basic test scripts:

python test_scripts/test_dashboard.py
python test_scripts/test_advisory.py cotton
python test_scripts/test_all.py


(If a script fails due to missing modules, reinstall dependencies.)

API Endpoints Summary
Public Endpoints

GET /

GET /fusion/health

Auth Required

Use:

Authorization: Bearer <your-jwt-token>


Get your token via /api/auth/login.

Troubleshooting
"Module not found"

Ensure you're inside backend/

Activate your .venv

Run pip install -r requirements.txt

Database issues

SQLite: folder must be writable

PostgreSQL: check your connection string

Tables generate on first app start

Port already in use

Use another port:
uvicorn app.main:app --reload --port 8001

CORS

Defaults to http://localhost:8080

Update in main.py if frontend URL differs

More Information

Fusion Engine Setup → FUSION_ENGINE_SETUP.md

Testing Guide → test_scripts/README.md

Database Migrations → migrations/README_MIGRATION.md

Full Documentation → ../docs/Agrisense_Documentation.md

Notes

Designed for React frontend

All endpoints return JSON

Errors follow a consistent structure

Fusion Engine uses rule-based JSON logic

External APIs are handled via the service modules
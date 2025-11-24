KrushiRakshak Backend
This is the backend part of the KrushiRakshak project. It’s made using FastAPI, and it basically handles all the stuff the frontend depends on — like user accounts, processing agri-data, running the Fusion Engine, and even the whole farmer community section.

(If you're checking different parts of the system, the Fusion Engine section usually gives a good idea of how everything ties together.)

What This Backend Does
• User Management: signup, login, updating profiles — all secured using JWT.
• Fusion Engine: takes weather, market prices, satellite NDVI data, etc., and creates crop advisories.
• Community Features: posts, likes, comments — all the social features go through here.
• AI Chatbot: connects with Google Gemini to answer farming-related queries.
• Data Services: pulls data from IMD, Agmarknet, Bhuvan and processes it for use.

Quick Start

Install Dependencies
Start by creating a virtual environment and installing everything from requirements.txt.

Windows (PowerShell)
python -m venv .venv
..venv\Scripts\Activate
pip install -r requirements.txt

Linux/Mac
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Set Up Environment Variables
Inside the backend/ folder, create a .env file (copy .env.example if it’s present).

SECRET_KEY=your-secret-key-here-make-it-long-and-random
DATABASE_URL=sqlite:///./agrisense_dev.db
GEMINI_API_KEY=your-google-gemini-api-key-optional

Important notes:
• SECRET_KEY → used for JWT, so keep it long and random.
• SQLite works perfectly fine for development and testing.
• Default DB is SQLite.
• For PostgreSQL:
postgresql://user:password@localhost/agrisense_db
• Gemini API key is optional unless you want the chatbot feature.

Run the Server
uvicorn app.main:app --reload --port 8000

Backend will be available at:
http://127.0.0.1:8000

Check API Documentation
• Swagger UI → http://127.0.0.1:8000/docs

• ReDoc → http://127.0.0.1:8000/redoc

You can test all endpoints directly from these pages.

Project Structure
backend/
├── app/
│ ├── main.py
│ ├── database.py
│ ├── models.py
│ ├── schemas.py
│ ├── crud.py
│ ├── auth.py
│ ├── fusion_engine.py
│ ├── community.py
│ ├── ai.py
│ ├── services/
│ │ ├── weather.py
│ │ ├── market.py
│ │ ├── ndvi.py
│ │ └── crop_stage.py
│ └── utils/
├── data/
│ ├── weather_data.json
│ ├── market_prices.json
│ ├── crop_health.json
│ └── crops_metadata.json
├── rules/
│ ├── pest_rules.json
│ ├── irrigation_rules.json
│ └── market_rules.json
├── etl/
│ └── make_features.py
├── test_scripts/
│ └── README.md
├── migrations/
├── requirements.txt
└── README.md

Main Components

Authentication (app/auth.py)
Handles user-related actions:
• POST /api/auth/signup
• POST /api/auth/login
• GET /api/auth/me
• PATCH /api/auth/profile

Fusion Engine (app/fusion_engine.py)
Responsible for:
• dashboard info
• crop-wise advisories

(The advisory logic depends on a rule set plus incoming sensor data.)

Endpoints include:
• /fusion/dashboard
• /fusion/advisory/{crop}

Community (app/community.py)
Handles all farmer interaction features:
• get posts
• create post
• like
• comment

AI Chatbot (app/ai.py)
Uses Gemini AI:
• POST /ai/chat

Database
By default the app uses SQLite:
agrisense_dev.db
Good for development.

For production, switch to PostgreSQL:
DATABASE_URL=postgresql://username:password@localhost/agrisense_db

Tables get created automatically the first time the app starts.

Testing
Use the test scripts to check if everything’s fine:
python test_scripts/test_dashboard.py
python test_scripts/test_advisory.py cotton
python test_scripts/test_all.py

More info in test_scripts/README.md.

API Endpoints Summary

Public
• GET /
• GET /fusion/health

Require JWT
Use header:
Authorization: Bearer <your-jwt-token>

Login using /api/auth/login to get the token.

Troubleshooting

Module not found
• Make sure you're inside backend/
• Activate your venv
• Install requirements again

Database errors
• SQLite: check folder permissions
• PostgreSQL: verify connection string
• Tables auto-create

Port already in use
uvicorn app.main:app --reload --port 8001

CORS issues
Default CORS allows localhost:8080.
Update settings in main.py if frontend uses a different URL.

More Information
• Fusion Engine setup → FUSION_ENGINE_SETUP.md
• Testing guide → test_scripts/README.md
• Migration notes → migrations/README_MIGRATION.md
• Full docs → ../docs/Agrisense_Documentation.md

Notes
• Designed to work smoothly with the React frontend
• All responses are in JSON
• Error format is consistent
• Fusion Engine uses JSON rule files
• API integrations happen through app/services/
• External APIs are handled by dedicated service modules
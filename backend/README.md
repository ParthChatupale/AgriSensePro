# KrushiRakshak Backend

This is the backend server for KrushiRakshak, built with FastAPI. It handles user authentication, processes agricultural data, runs the Fusion Engine, and manages the community features.

## What This Backend Does

- **User Management**: Sign up, login, and profile management with secure JWT authentication
- **Fusion Engine**: Combines weather, market, and satellite data to generate crop advisories
- **Community Features**: Handles posts, comments, and likes for the farmer community
- **AI Chatbot**: Integrates with Google Gemini for answering farming questions
- **Data Services**: Fetches and processes data from IMD, Agmarknet, and Bhuvan APIs

## Quick Start

### 1. Install Dependencies

First, create a virtual environment and install the required packages:

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the `backend/` folder (you can copy from `.env.example` if it exists):

```env
SECRET_KEY=your-secret-key-here-make-it-long-and-random
DATABASE_URL=sqlite:///./agrisense_dev.db
GEMINI_API_KEY=your-google-gemini-api-key-optional
```

**Important**: 
- `SECRET_KEY` is used for JWT token signing - make it long and random
- `DATABASE_URL` defaults to SQLite. For PostgreSQL, use: `postgresql://user:password@localhost/agrisense_db`
- `GEMINI_API_KEY` is only needed if you want to use the AI chatbot feature

### 3. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`

### 4. Check API Documentation

Open your browser and visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

These pages show all available endpoints and let you test them directly.

## Project Structure

<img width="512" height="768" alt="image" src="https://github.com/user-attachments/assets/7a17385e-dced-4177-aa91-036e43bef13e" />

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database connection and session setup
│   ├── models.py            # SQLAlchemy database models (User, Post, etc.)
│   ├── schemas.py           # Pydantic models for request/response validation
│   ├── crud.py              # Database helper functions
│   ├── auth.py              # Authentication routes (signup, login, profile)
│   ├── fusion_engine.py     # Fusion Engine router (dashboard, advisory)
│   ├── community.py         # Community features (posts, comments, likes)
│   ├── ai.py                # AI chatbot integration
│   ├── services/            # External API integration services
│   │   ├── weather.py       # IMD weather data fetching
│   │   ├── market.py        # Agmarknet market price fetching
│   │   ├── ndvi.py          # Bhuvan satellite data processing
│   │   └── crop_stage.py    # Crop growth stage detection
│   └── utils/               # Helper utilities
├── data/                    # JSON data files (mock data for development)
│   ├── weather_data.json
│   ├── market_prices.json
│   ├── crop_health.json
│   └── crops_metadata.json
├── rules/                   # Rule definitions for Fusion Engine
│   ├── pest_rules.json      # Pest detection rules
│   ├── irrigation_rules.json # Irrigation trigger rules
│   └── market_rules.json     # Market risk detection rules
├── etl/                     # Data processing scripts
│   └── make_features.py     # Rule evaluation engine
├── test_scripts/            # Testing scripts
│   └── README.md            # Test documentation
├── migrations/              # Database migration scripts
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Main Components

### Authentication (`app/auth.py`)
Handles user registration, login, and profile management:
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user profile
- `PATCH /api/auth/profile` - Update user profile

### Fusion Engine (`app/fusion_engine.py`)
The core intelligence system that generates advisories:
- `GET /fusion/dashboard` - Get combined dashboard data (weather, market, alerts)
- `GET /fusion/advisory/{crop}` - Get crop-specific advisory with recommendations

### Community (`app/community.py`)
Social features for farmers:
- `GET /api/community/posts` - Get all posts
- `POST /api/community/posts` - Create new post
- `POST /api/community/posts/{post_id}/like` - Like a post
- `POST /api/community/posts/{post_id}/comment` - Add comment

### AI Chatbot (`app/ai.py`)
AI-powered farming assistant:
- `POST /ai/chat` - Send message to AI chatbot

## Database

By default, the app uses SQLite (file: `agrisense_dev.db`). This is fine for development.

For production, switch to PostgreSQL by updating `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://username:password@localhost/agrisense_db
```

The database tables are automatically created when you first run the app (see `app/main.py`).

## Testing

We have test scripts to verify everything works:

```bash
# Test dashboard endpoint
python test_scripts/test_dashboard.py

# Test advisory endpoint
python test_scripts/test_advisory.py cotton

# Test all endpoints
python test_scripts/test_all.py
```

See `test_scripts/README.md` for more details.

## API Endpoints Summary

### Public Endpoints
- `GET /` - Welcome message
- `GET /fusion/health` - Health check

### Authentication Required
Most endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

Get a token by calling `/api/auth/login` with your email and password.

## Troubleshooting

### "Module not found" errors
- Make sure you're in the `backend/` directory
- Activate your virtual environment
- Run `pip install -r requirements.txt`

### Database errors
- If using SQLite, make sure the `backend/` folder is writable
- If using PostgreSQL, check your connection string in `.env`
- Tables are auto-created on first run

### Port already in use
- Change the port: `uvicorn app.main:app --reload --port 8001`
- Or stop the other process using port 8000

### CORS errors (from frontend)
- CORS is already configured in `app/main.py` to allow requests from `http://localhost:8080`
- If using a different frontend URL, update the CORS settings

## More Information

- **Fusion Engine Details**: See `FUSION_ENGINE_SETUP.md`
- **Testing Guide**: See `test_scripts/README.md`
- **Database Migrations**: See `migrations/README_MIGRATION.md`
- **Complete Documentation**: See `../docs/Agrisense_Documentation.md`

## Notes

- The backend is designed to work with the React frontend
- All endpoints return JSON
- Error responses follow a consistent format
- The Fusion Engine uses rule-based logic stored in JSON files
- External API calls are made through service modules in `app/services/`

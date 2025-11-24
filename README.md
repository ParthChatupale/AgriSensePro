# KrushiRakshak

A smart farming platform that helps Indian farmers make better decisions by combining weather data, satellite images, market prices, and expert knowledge into one easy-to-use app.

## What is KrushiRakshak?

KrushiRakshak is a web application built for farmers who need quick, reliable information about their crops. Instead of checking multiple websites or apps, farmers can see everything they need in one place: weather forecasts, crop health status, market prices, and personalized advice.

The app works even when internet is slow or unavailable, making it perfect for rural areas. It's available in multiple languages and designed to be simple enough for anyone to use.

## Key Features

- **Real-Time Dashboard**: See weather, market prices, crop health, and alerts all in one screen
- **Fusion Engine**: Our smart system combines different data sources to give you accurate crop advice
- **Crop Advisories**: Get personalized recommendations for pest control, irrigation, and crop care
- **Market Intelligence**: Track price trends to know the best time to sell your produce
- **Community Forum**: Share experiences and learn from other farmers
- **AI Chatbot**: Ask farming questions anytime and get instant answers
- **Offline Support**: Works without internet using cached data
- **Multi-Language**: Available in English and Marathi (more languages coming soon)

## Why This System Feels Different

- **Hybrid Fusion Engine**: Typical dashboards lean only on rules or only on ML. We run both. Hand-crafted agronomy rules keep the system transparent, and lightweight models provide extra context, so an alert is both explainable and confident.
- **Community Built In**: Farmers don’t need separate chat groups. The community page lets them post photos, describe issues, and get responses from peers or extension teams. Those conversations also help us refine the advisory logic.

### Impact on the Ground

- Alerts land faster because they’re backed by both data science and agronomy know-how.
- Discussions stay inside KrushiRakshak, giving mentors and agri experts one place to watch emerging issues.
- The balanced approach cuts down on noisy alerts and keeps the experience easy to trust.

## System Architecture

KrushiRakshak is organized into four practical layers so the whole story fits inside one diagram.

1. **Layer 1 – Farmer Web App**: React PWA that works offline (IndexedDB + service worker), shows the dashboard, lets farmers share updates, and captures photo + GPS inputs.
2. **Layer 2 – Middleware / API**: FastAPI handles authentication (JWT), routes Fusion Engine requests, and issues push or SMS alerts when severity is high.
3. **Layer 3 – Intelligence & Analysis**: ETL jobs keep a feature store fresh, then the Fusion Engine blends ML scores with rule-based logic before the advisory generator packages the final response.
4. **Layer 4 – Infrastructure & Storage**: PostgreSQL/PostGIS, MinIO/S3 buckets, and the monitoring/admin panel keep data, media, and operations in one place.

External feeds (IMD weather, Agmarknet prices, Bhuvan NDVI, Gemini AI) sit under the diagram and drive the intelligence layer.

### How It Works

<img width="1723" height="969" alt="image" src="https://github.com/user-attachments/assets/d16edb5d-5c98-4622-8327-eaf0c7ee3287" />


### Data Flow

1. **User opens the app** → Frontend loads dashboard
2. **Frontend requests data** → Backend receives request
3. **Backend fetches data** → Calls weather, market, and satellite APIs
4. **Fusion Engine processes** → Combines all data and applies rules
5. **Advisory generated** → Personalized recommendations created
6. **Response sent** → Frontend displays results to user
7. **Data cached** → Stored for offline use

### Core Components

#### 1. Fusion Engine
The brain of our system. It takes data from weather, market, and satellite sources and combines them using rules to detect:
- Pest risks (high humidity + temperature = pest alert)
- Irrigation needs (low soil moisture = water needed)
- Market opportunities (price trends = best time to sell)

#### 2. Rule-Based System
We use simple rules written in JSON files that check conditions like:
- "If temperature > 32°C AND humidity > 70%, then pest risk is HIGH"
- "If soil moisture < 30%, then irrigation needed"
- "If price dropped 10% in 7 days, then market alert"

#### 3. Dashboard
Shows everything at a glance:
- Current weather (temperature, rain, wind)
- Market prices with trend arrows
- Crop health status (NDVI values)
- Active alerts with confidence scores
- Quick links to detailed advisories

#### 4. Advisory System
Generates crop-specific advice based on:
- Your location (weather conditions)
- Your crop type (cotton, wheat, rice, etc.)
- Current crop stage (vegetative, flowering, etc.)
- Recent data trends

## Technology Stack

### Frontend
- **React + TypeScript**: Modern web framework for building user interfaces
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS for quick styling
- **shadcn/ui**: High-quality component library
- **PWA**: Service workers for offline functionality

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database toolkit and ORM
- **SQLite/PostgreSQL**: Database for storing user data
- **JWT**: Secure authentication tokens

### External Services
- **IMD Weather API**: Government weather data
- **Agmarknet API**: Official market price data
- **Bhuvan Satellite**: ISRO satellite imagery for crop health
- **Google Gemini**: AI chatbot for farming questions

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd agrisense
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   python -m venv .venv
   # Windows:
   .venv\Scripts\Activate
   # Linux/Mac:
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env` in the backend folder
   - Add your API keys (weather, market, AI chatbot)
   - See `backend/README.md` for details

5. **Start the backend server**
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

6. **Start the frontend (in a new terminal)**
   ```bash
   npm run dev
   ```

7. **Open your browser**
   - Frontend: http://localhost:8080
   - Backend API docs: http://localhost:8000/docs

## Project Structure

```
agrisense/
├── src/                     # React + TypeScript PWA
│   ├── components/          # Shared UI (shadcn/ui)
│   ├── pages/               # Home, Dashboard, Community, etc.
│   ├── services/            # API client + auth helpers
│   └── i18n/, hooks/, context/, lib/…
├── public/                  # Static assets + PWA manifest
├── backend/                 # FastAPI service (fusion engine, community, alerts)
│   ├── app/                 # Routers, models, services
│   ├── data/                # Weather/market/NDVI JSON feeds
│   ├── rules/               # Rule configs (pest/irrigation/market)
│   ├── etl/                 # Feature builder scripts
│   ├── test_scripts/        # API sanity tests
│   └── … (uploads/, templates/, migrations/, etc.)
├── docs/                    # Demo scripts + deep-dive documentation
├── dist/ , dev-dist/        # Production build artifacts (frontend/PWA)
├── configuration files      # package.json, tailwind.config.ts, tsconfig*.json, vite.config.ts, eslint.config.js
└── README.md                # This file
```

Need the full FastAPI tree? Check [`backend/README.md`](backend/README.md) for the complete breakdown.

## Detailed Documentation

For more detailed information about specific parts of the system, check out these documentation files:

- **`docs/Agrisense_Documentation.md`**: Complete technical documentation covering all features, APIs, and architecture
- **`backend/README.md`**: Backend setup and development guide
- **`backend/FUSION_ENGINE_SETUP.md`**: How the Fusion Engine works and how to configure rules
- **`backend/test_scripts/README.md`**: How to test the backend endpoints
- **`INTEGRATION_GUIDE.md`**: Guide for integrating user crop and location features
- **`docs/DEMO_SCRIPT.md`**: Script for demonstrating the system
- **`docs/dashboardscript.md`**: Detailed dashboard walkthrough

## Development

### Running Tests
```bash
# Frontend tests
npm run test

# Backend tests
cd backend
pytest app/tests
```

### Building for Production
```bash
# Frontend
npm run build
# Output in dist/ folder

# Backend
# Deploy FastAPI app to your hosting service
```

## Deployment

### Frontend
1. Build the app: `npm run build`
2. Deploy the `dist/` folder to any static hosting:
   - Netlify
   - Vercel
   - AWS S3 + CloudFront
   - GitHub Pages

### Backend
1. Set up environment variables on your hosting service
2. Deploy FastAPI app to:
   - Render
   - Railway
   - Heroku
   - AWS EC2
   - Azure App Service

3. Update frontend `config.ts` with your backend URL

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`npm run lint`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

Copyright © 2025 KrushiRakshak. All rights reserved.

## Support

For questions or issues, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for Indian farmers**

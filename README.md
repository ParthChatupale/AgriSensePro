# KrushiRakshak

KrushiRakshak is basically a smart farming platform we built to make life easier for Indian farmers. The goal is simple: pull weather data, satellite readings, market prices, and expert knowledge into one place so farmers don’t have to juggle five different apps.

## What is KrushiRakshak?

KrushiRakshak is a web app for farmers who want quick, reliable updates about their crops. Instead of hopping between different sites, they can check everything here—weather, crop health, prices, and personalized advice. The app still works when the internet is slow or drops off (pretty common in rural areas). It supports multiple languages and we’ve tried to keep the interface straightforward.

## Key Features

- **Real-Time Dashboard**: Weather, crop status, alerts, and prices on one screen.
- **Fusion Engine**: Combines weather, NDVI, market data, and crop stage before suggesting anything.
- **Crop Advisories**: Targeted guidance for irrigation, pest control, and overall crop care.
- **Market Intelligence**: Tracks price momentum so farmers can time their sales.
- **Community Forum**: Farmers can post photos, ask questions, and help each other.
- **AI Chatbot**: Let’s you ask farming questions anytime of day.
- **Offline Support**: Works from cached data when connectivity disappears.
- **Multi-Language**: Currently English + Marathi, more coming later.
## Why This System Feels Different

- **Hybrid Fusion Engine**: Most dashboards rely only on rules or only on ML. We use both. Rules keep the system explainable; lightweight models add confidence and context so alerts don’t feel like guesswork.
- **Built-in Community**: Farmers don’t need random group chats. The community space lets them upload crop issues, talk to others, and get help. Those conversations also feed back into the advisory logic over time.

### Impact on the Ground

- Alerts trigger faster because they mix agronomy knowledge with real-time data.
- Farmers and experts can talk inside the same app, which makes it easier to track outbreaks.
- The balanced approach reduces noisy alerts and builds trust.
## System Architecture

KrushiRakshak is broken into four easy-to-follow layers:

1. **Layer 1 – Farmer Web App**: React PWA with offline mode (IndexedDB + service worker). Shows the dashboard, handles photo/GPS uploads, and powers the community space.
2. **Layer 2 – Middleware / API**: FastAPI handles authentication (JWT), routes Fusion Engine calls, and pushes SMS/push alerts when risk is high.
3. **Layer 3 – Intelligence & Analysis**: ETL jobs keep features fresh, then the Fusion Engine blends rules + ML before packing the advisory response.
4. **Layer 4 – Infrastructure & Storage**: PostgreSQL/PostGIS for data, MinIO/S3 for media, plus monitoring/admin tools.

External feeds like IMD weather, Agmarknet prices, Bhuvan NDVI, and Gemini AI feed into the intelligence layer. We cache data so the UI doesn’t blank out if an API hiccups.
### How It Works

<img width="1723" height="969" alt="image" src="https://github.com/user-attachments/assets/d16edb5d-5c98-4622-8327-eaf0c7ee3287" />

### Data Flow

1. Farmer opens the app → dashboard loads.
2. Frontend asks backend for fresh info.
3. Backend collects weather, market, and satellite data.
4. Fusion Engine processes everything and runs rules.
5. Advisory gets generated based on the combined data.
6. Backend sends results → frontend shows them.
7. Data is cached locally so it works offline later.

### Core Components

1. **Fusion Engine**  
   Analyzes weather, market, and satellite signals to detect pest risks, irrigation needs, and price opportunities.
2. **Rule-Based System**  
   Simple JSON rules run checks (e.g., temp/humidity thresholds, soil moisture alerts, price drops).
3. **Dashboard**  
   Shows current weather, price trends, crop health, alerts, and shortcuts to full advisories.
4. **Advisory System**  
   Combines location, crop type, crop stage, and recent trends before suggesting next steps.
## Technology Stack

### Frontend
- React + TypeScript  
- Vite  
- Tailwind CSS  
- shadcn/ui components  
- PWA with offline capability

### Backend
- FastAPI  
- SQLAlchemy  
- SQLite/PostgreSQL  
- JWT authentication

### External Services
- IMD Weather API  
- Agmarknet API  
- Bhuvan Satellite NDVI  
- Google Gemini for Q&A
## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Git

### Installation

1. Clone repo  
   ```bash
   git clone https://github.com/ParthChatupale/AgriSensePro.git
   cd agrisense
   ```
2. Install frontend deps  
   ```bash
   npm install
   ```
3. Install backend deps  
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\Activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   ```
4. Environment variables  
   - Copy `.env.example` → `.env`
   - Add API keys (weather, market, AI)
5. Start backend  
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
6. Start frontend  
   ```bash
   npm run dev
   ```
7. Open in browser  
   - Frontend: <http://localhost:8080>  
   - Backend docs: <http://localhost:8000/docs>

## Project Structure

```markdown
agrisense/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── i18n/, hooks/, context/, lib/…
├── public/
├── backend/
│   ├── app/
│   ├── data/
│   ├── rules/
│   ├── etl/
│   ├── test_scripts/
│   └── uploads/, templates/, migrations/
├── docs/
├── dist/, dev-dist/
├── config files
└── README.md
```

Need the full FastAPI tree? See [`backend/README.md`](backend/README.md).

## Detailed Documentation

- `docs/Agrisense_Documentation.md`
- `backend/README.md`
- `backend/FUSION_ENGINE_SETUP.md`
- `backend/test_scripts/README.md`
- `INTEGRATION_GUIDE.md`
- `docs/DEMO_SCRIPT.md`
- `docs/dashboardscript.md`

## Development

### Running Tests

```bash
npm run test        # frontend
cd backend && pytest app/tests
```

### Production Builds

```bash
# Frontend bundle
npm run build

# Backend: deploy FastAPI using your hosting target
```

## Deployment

### Frontend
- Build with `npm run build` and deploy `dist/` to Netlify, Vercel, AWS S3/CloudFront, GitHub Pages, etc.

### Backend
- Configure environment variables (same keys as `.env`).
- Deploy FastAPI to Render, Railway, Heroku, AWS EC2, Azure App Service, etc.
- Update the frontend `config.ts` with the live backend URL.

## Contributing

1. Fork the repo
2. Create a branch (`git checkout -b feature/xyz`)
3. Make changes
4. Run tests (`npm run lint`, `npm run test`)
5. Commit (`git commit -m "feat: ... "`)
6. Push (`git push origin feature/xyz`)
7. Open a PR

## License

Copyright © 2025 KrushiRakshak

## Support

Open an issue on GitHub or reach out to the team if you’re stuck.


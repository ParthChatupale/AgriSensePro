# krushiRakshak / AgriSense

Smart farming assistant that unifies weather, satellite imagery, market data, and community knowledge to deliver crop-aware insights for Indian farmers.

## Features

- Real-time dashboard with IMD weather, Agmarknet market trends, NDVI trends, and risk alerts
- Fusion Engine backend that fuses datasets and applies rule-based agronomy logic (pest, irrigation, market)
- Farmer advisory workflows, multilingual UI, offline-ready PWA shell, and community forum

## Tech Stack

- Frontend: Vite, React, TypeScript, Tailwind CSS, shadcn/ui, PWA
- Backend: FastAPI, SQLite (via SQLModel), ETL scripts for weather/market/NDVI data
- Tooling: ESLint, Playwright + Vitest for automated checks

## Development

```sh
git clone <repo-url>
cd agrisense
npm install
npm run dev      # frontend at http://localhost:8080

# backend (from ./backend)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Environment variables (create `.env` files) cover API keys for weather, market, Firebase auth, and optional storage providers. See `src/config.ts` and `backend/README.md` for required settings.

## Deployment

1. Frontend: `npm run build` → deploy `dist/` to any static host (Netlify, Vercel, S3+CloudFront, etc.).
2. Backend: Deploy FastAPI app to Render, Railway, Azure, or on-prem; set `FUSION_ENGINE_URL` env for frontend to target the deployed API.
3. Configure HTTPS and service workers for full PWA offline support.

## Testing

- Frontend unit/UI: `npm run test`
- End-to-end smoke tests: `npm run test:e2e`
- Backend suite: `pytest backend/app/tests`

## Contributing

1. Fork & create a feature branch.
2. Follow conventional commits and run formatters/lints (`npm run lint`, `ruff check`, `black`).
3. Open a PR with context, screenshots, or API samples when relevant.

## License

Copyright © 2025 AgriSense.

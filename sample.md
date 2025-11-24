# KrushiRakshak System Architecture (Sample)

This document gives judges an easy-to-scan overview of how KrushiRakshak is wired. It explains every layer at a glance using plain language and a refreshed diagram.

---

## 📐 Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                            USER DEVICES                               │
│  PWA in browser / installed app (React + TypeScript + shadcn/ui)      │
│  - Pages: Home, Dashboard, Advisory, Community, Profile, Report       │
│  - Works offline via service worker cache + IndexedDB storage         │
│  - Talks to backend through REST calls (JSON over HTTPS)              │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                │ HTTPS (JWT secured)
                                │
┌───────────────────────────────▼──────────────────────────────────────┐
│                         FASTAPI BACKEND                              │
│  - Auth Router (signup, login, profile, JWT issuing)                 │
│  - Fusion Engine Router (dashboard + advisory endpoints)             │
│  - Community Router (posts, comments, likes, media uploads)          │
│  - AI Router (Gemini-powered chatbot endpoint)                       │
│                                                                      │
│  Supporting Layers:                                                  │
│  • Services (weather, market, NDVI, geocoding, crop stage)           │
│  • Rules Engine (pest/irrigation/market JSON specs)                  │
│  • Task scripts / ETL helpers for feature prep                       │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                │ SQLAlchemy ORM
                                │
┌───────────────────────────────▼──────────────────────────────────────┐
│                           DATA STORAGE                               │
│  Primary: SQLite (dev) / PostgreSQL (prod)                           │
│  Tables: users, posts, comments, post_likes, cached_market, alerts   │
│                                                                      │
│  Files: JSON datasets for crops, rules, mock weather/market samples   │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                │ Outbound API calls / Scheduler pulls
                                │
┌───────────────────────────────▼──────────────────────────────────────┐
│                      EXTERNAL DATA SOURCES                           │
│  - IMD / Open-Meteo → weather + forecasts                            │
│  - Agmarknet → mandi prices + trends                                 │
│  - Bhuvan / synthetic NDVI → vegetation health                       │
│  - Nominatim → reverse geocoding for village/state/district          │
│  - Google Gemini → conversational answers                            │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Fusion Engine Flow

1. **Collect Inputs**
   - Weather, NDVI, soil moisture, markets, crop metadata, user profile.
2. **Build Feature Vector**
   - Smooth NDVI series, compute deltas, stage detection, humidity/temperature indices.
3. **Evaluate Rules**
   - Pest, irrigation, and market rule bundles fire based on thresholds.
4. **Score & Prioritize**
   - Winning rule sets severity (high/medium/low) and confidence (%).
5. **Assemble Response**
   - Advisory summary, triggered rules, recommended actions, metrics, data sources.

---

## 🔐 Security & Reliability Notes

- JWT protects every authenticated route (dashboard, advisory, posts, profile).
- CORS locked to known origins (`localhost:8080` etc.).
- Service worker provides offline-first UX and background sync.
- Pydantic validation ensures every request/response stays well-typed.

---

## ✅ What This Diagram Highlights

- Clear handoff between PWA, FastAPI, database, and third-party feeds.
- Modular routers keep auth, intelligence, community, and AI cleanly separated.
- Rules + ML-ready services allow transparent advisory generation.
- Offline + multilingual capabilities live entirely in the frontend layer.

Use this page as a print-ready artifact during demos or submission decks.


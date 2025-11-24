
   # ✅ What’s Already Connected

### Data packs
`backend/data/` contains crop metadata, sample weather snapshots, NDVI health info, market prices, and alert templates—everything the engine needs.

### Rule definitions
Rules live in `backend/rules/` (pest, irrigation, market) and support `>`, `<`, `>=`, `<=`, `==`, `!=`, `abs_gte`.

### Feature builder
`backend/etl/make_features.py` loads JSON inputs, computes derived values, and applies rules sequentially.

### FastAPI routes
Already exposed via:

- `GET /fusion/dashboard`
- `GET /fusion/advisory/{crop}`

`backend/app/main.py` wires the router, so nothing extra is needed.

### Test scripts
`backend/test_scripts/` holds ready-made scripts plus a README with expected outputs.

### Frontend usage
React dashboard + advisory pages hit these endpoints via `src/services/api.ts` and `src/types/fusion.ts`.

---

## 🚀 Quick Start

Start the backend:

```bash
cd agrisense/backend
uvicorn app.main:app --reload
```

Run basic tests:

```bash
# Dashboard test
python test_scripts/test_dashboard.py

# Advisory test for cotton
python test_scripts/test_advisory.py cotton

# Run everything
python test_scripts/test_all.py
```

API docs UI: <http://localhost:8000/docs>

---

## 📊 Endpoint Details

### `GET /fusion/dashboard`

Returns:

- Weather (temp, humidity, rainfall, wind)
- Market prices (wheat, rice, cotton, sugarcane)
- Alerts list (pest, irrigation, market)
- Crop health summary
- Overall stats

### `GET /fusion/advisory/{crop}`

Includes:

- Crop name, severity, priority
- Overall analysis
- Triggered rules
- Recommendations with priorities
- Rule breakdown (pest/irrigation/market scores)
- Data sources (IMD, Bhuvan, Agmarknet)

---

## 🔧 Rule Operators

- `>` greater than
- `<` less than
- `>=` greater or equal
- `<=` less or equal
- `==` equal
- `!=` not equal
- `abs_gte` absolute value ≥ threshold (useful for NDVI change)

---

## 📁 Key Files

```bash
backend/
├── app/
│   ├── fusion_engine.py      # Main router
│   └── main.py               # App with router wired
├── data/
│   ├── crops_metadata.json
│   ├── weather_data.json
│   ├── crop_health.json
│   ├── market_prices.json
│   └── alerts.json
├── rules/
│   ├── pest_rules.json
│   ├── irrigation_rules.json
│   └── market_rules.json
├── etl/
│   └── make_features.py
└── test_scripts/
    ├── test_dashboard.py
    ├── test_advisory.py
    ├── test_all.py
    └── README.md
```

Additional folders:

- `uploads/` — farmer photos for community/advisory
- `templates/` — advisory PDFs and snippets
- `migrations/` — SQL scripts + helpers

---

## 🎯 Example Rule

```json
{
  "significant_ndvi_change": {
    "description": "Significant NDVI change (positive or negative) indicates stress",
    "conditions": [
      { "feature": "ndvi_change", "op": "abs_gte", "value": 0.08 }
    ],
    "score": 0.7,
    "recommendation": "Investigate cause of significant NDVI change",
    "severity": "medium"
  }
}
```

Fires when `abs(ndvi_change) >= 0.08`, flagging noticeable NDVI spikes or drops.

---

## ✅ Sanity Checklist

- JSON files under `backend/data/` load correctly.
- Rules exist for pest, irrigation, market.
- `make_features.py` evaluates every operator (including `abs_gte`).
- Fusion router registered in `backend/app/main.py`.
- Dashboard + advisory tests succeed.
- Frontend fusion types match API output.

---

## 🐛 Troubleshooting

- **Import error**: Activate venv and ensure you’re inside `backend/`.
- **Missing file**: Confirm JSON exists under `backend/data/` (case sensitive).
- **API unreachable**: Check if `uvicorn` runs on port 8000.
- **Rule not firing**: Feature names must match exactly (`ndvi_change` vs `NDVIChange` will fail).

   

# Fusion Engine Setup Guide

Use this page as a quick reference when you want to check that the advisory flow is ready end-to-end.

## ✅ What’s Already Hooked Up

1. **Data packs in place**  
   `backend/data/` bundles crop metadata, sample weather snapshots, NDVI health data, market prices, and alert templates.
2. **Rule definitions**  
   `backend/rules/` holds pest, irrigation, and market rule sets. Every rule understands the same operators (`>`, `<`, `>=`, `<=`, `==`, `!=`, `abs_gte`).
3. **Feature builder**  
   `backend/etl/make_features.py` loads those JSON feeds, calculates derived metrics, and applies the rules.
4. **FastAPI routes**  
   `backend/app/fusion_engine.py` publishes:
   - `GET /fusion/dashboard`
   - `GET /fusion/advisory/{crop}`
   The router is already registered in `backend/app/main.py`.
5. **Test scripts**  
   Dashboard, advisory, and full-suite scripts live in `backend/test_scripts/` with a README that explains expected output.
6. **Frontend consumers**  
   The React dashboard/advisory pages plus `src/services/api.ts` and `src/types/fusion.ts` depend on these endpoints today.

## 🚀 Quick Start

### Start the backend
```bash
cd agrisense/backend
uvicorn app.main:app --reload
```

### Smoke-test the endpoints
```bash
# Test dashboard
python test_scripts/test_dashboard.py

# Test advisory for cotton
python test_scripts/test_advisory.py cotton

# Test all endpoints
python test_scripts/test_all.py
```

### Explore via docs UI
Open http://localhost:8000/docs

## 📊 Endpoint Details

### GET /fusion/dashboard
Returns:
- Weather data (temperature, humidity, rainfall, wind)
- Market prices (wheat, rice, cotton, sugarcane)
- Alerts list (pest, irrigation, market)
- Crop health summary
- Summary statistics

### GET /fusion/advisory/{crop}
Returns:
- Crop name, priority, severity
- Analysis summary
- Fired rules list
- Recommendations with priorities
- Rule breakdown (pest/irrigation/market scores)
- Data sources (IMD, Bhuvan, Agmarknet)

## 🔧 Rule Operators

Supported operators in rule conditions:
- `>` - Greater than
- `<` - Less than
- `>=` - Greater than or equal
- `<=` - Less than or equal
- `==` - Equal to
- `!=` - Not equal to
- `abs_gte` - Absolute value greater than or equal (e.g., for NDVI changes)

## 📁 Key Files

```
backend/
├── app/
│   ├── fusion_engine.py      # Main router
│   └── main.py               # App with router wired
├── data/
│   ├── crops_metadata.json   # Crop information
│   ├── weather_data.json     # Weather data
│   ├── crop_health.json      # Crop health data
│   ├── market_prices.json    # Market prices
│   └── alerts.json           # Alert definitions
├── rules/
│   ├── pest_rules.json       # Pest detection rules
│   ├── irrigation_rules.json # Irrigation rules
│   └── market_rules.json     # Market rules
├── etl/
│   └── make_features.py      # Rule evaluation engine
└── test_scripts/
    ├── test_dashboard.py     # Dashboard tests
    ├── test_advisory.py      # Advisory tests
    ├── test_all.py           # All tests
    └── README.md             # Test docs

    # Additional directories used day-to-day
├── uploads/                  # Farmer photos used by community/advisory flows
├── templates/                # Advisory PDFs + explanation snippets
└── migrations/               # SQL scripts and helpers
```

## 🎯 Example Rule

```json
{
  "significant_ndvi_change": {
    "description": "Significant NDVI change (positive or negative) indicates stress",
    "conditions": [
      {"feature": "ndvi_change", "op": "abs_gte", "value": 0.08}
    ],
    "score": 0.7,
    "recommendation": "Investigate cause of significant NDVI change",
    "severity": "medium"
  }
}
```

This rule fires when `abs(ndvi_change) >= 0.08`, meaning any significant change (positive or negative) in NDVI.

## ✅ Sanity Checklist

- [x] JSON packs under `backend/data/` parse cleanly.
- [x] Rule packs cover pest, irrigation, and market categories.
- [x] `make_features.py` can evaluate every operator, including `abs_gte`.
- [x] `backend/app/main.py` registers the fusion router.
- [x] Dashboard/advisory test scripts succeed.
- [x] Frontend types (`src/types/fusion.ts`) match the API responses.

## 🐛 Troubleshooting

1. **Import error**  
   Make sure you run commands from the `backend/` directory with the virtual environment activated.
2. **Missing data file**  
   Confirm the expected JSON lives under `backend/data/`; repo paths are case sensitive.
3. **API not reachable**  
   Ensure `uvicorn` is running on port 8000 and the port isn’t blocked.
4. **Rule never fires**  
   Double-check feature keys in the input payload. Names must match the rule definition exactly.


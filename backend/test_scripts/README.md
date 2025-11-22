# Backend Test Scripts

Simple test scripts to check if the backend API endpoints are working correctly. These scripts help verify that the Fusion Engine, dashboard, and advisory features are functioning as expected.

## Prerequisites

1. Install required Python packages:
   ```bash
   pip install requests
   ```

2. Start the FastAPI backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

## Test Scripts

### 1. Test Dashboard Endpoint

Tests the `/fusion/dashboard` endpoint:

```bash
python test_scripts/test_dashboard.py
```

**Expected Output:**
- Status code 200
- Weather data (temperature, humidity, rainfall, wind)
- Market prices for all crops
- Alerts list
- Crop health summary

### 2. Test Advisory Endpoint

Tests the `/fusion/advisory/{crop}` endpoint for a specific crop:

```bash
# Test cotton advisory
python test_scripts/test_advisory.py cotton

# Test wheat advisory
python test_scripts/test_advisory.py wheat

# Test rice advisory
python test_scripts/test_advisory.py rice
```

**Expected Output:**
- Status code 200
- Crop name, priority, severity
- Analysis summary
- Fired rules list
- Recommendations with priorities
- Rule breakdown (pest/irrigation/market scores)
- Data sources

### 3. Test AI Chatbot Endpoint

Tests the `/ai/chat` endpoint with Google Gemini 2.5 Pro:

```bash
# Test with default message
python test_scripts/test_ai_chatbot.py

# Test with custom message
python test_scripts/test_ai_chatbot.py "What is the best time to plant rice?"

# Test by directly importing module (bypasses HTTP)
python test_scripts/test_ai_chatbot.py --direct

# Test multiple different messages
python test_scripts/test_ai_chatbot.py --multiple
```

**Prerequisites:**
- `GEMINI_API_KEY` must be set in `.env` file
- `google-generativeai` package must be installed: `pip install google-generativeai`

**Expected Output:**
- Status code 200
- AI-generated response from Gemini 2.5 Pro
- Response should be farmer-friendly agricultural advice

### 4. Test All Endpoints

Runs comprehensive tests for dashboard and all crop advisories:

```bash
python test_scripts/test_all.py
```

**Tests:**
- Dashboard endpoint
- Advisory endpoint for cotton
- Advisory endpoint for wheat
- Advisory endpoint for rice

## Example Output

### Successful Test
```
✅ SUCCESS: Dashboard data retrieved

📊 Summary:
  - Total Alerts: 3
  - High Priority: 1
  - Crops Monitored: 3

🌤️  Weather:
  - Temperature: 30°C
  - Humidity: 75%
  - Rainfall: 12mm
  - Wind Speed: 8 km/h
```

### Failed Test
```
❌ ERROR: Could not connect to server.
   Make sure the backend is running at http://localhost:8000
   Start it with: uvicorn app.main:app --reload
```

## Troubleshooting

1. **Connection Error**: Make sure the backend server is running on `http://localhost:8000`
2. **404 Error**: Check that the data files exist in `backend/data/` directory
3. **500 Error**: Check backend logs for JSON parsing or file reading errors
4. **Import Error**: Make sure you're running from the `backend/` directory
5. **AI Chatbot Error**: 
   - Make sure `GEMINI_API_KEY` is set in `.env` file
   - Verify `google-generativeai` is installed: `pip install google-generativeai`
   - Check that the API key is valid and has access to Gemini 2.5 Pro
   - Check backend logs for detailed error messages from Gemini API

## Notes

- All test scripts use a 10-second timeout
- Tests are designed to be run while the backend is running
- Test scripts print both summary and full JSON responses
- Exit code 0 = success, exit code 1 = failure


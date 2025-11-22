# User Crop & Location Integration Guide

## ✅ Implementation Complete

This guide provides all code changes, SQL migrations, and testing instructions for integrating persistent user crop and location into KrushiRakshak.

---

## 📋 Files Modified

### Backend Files

1. **`backend/app/models.py`** - Added `crop` and `location` fields
2. **`backend/app/schemas.py`** - Added `UserUpdate` schema and crop/location to existing schemas
3. **`backend/app/crud.py`** - Added `update_user()` function, updated `create_user()` to handle crop/location
4. **`backend/app/auth.py`** - Added `PATCH /auth/profile` endpoint, updated signup/login to return crop/location
5. **`backend/app/fusion_engine.py`** - Added optional `crop` query parameter to `/fusion/dashboard`
6. **`backend/app/main.py`** - Replaced in-memory endpoints with auth router

### Frontend Files

1. **`src/pages/Profile.tsx`** - Added crop dropdown, location input with geolocate button, profile update API call
2. **`src/pages/Dashboard.tsx`** - Loads user crop and passes to dashboard API, highlights user's crop card
3. **`src/pages/Advisory.tsx`** - Defaults to user's crop if no URL param
4. **`src/services/api.ts`** - Added `updateProfile()` function, updated `getCurrentUser()` to use `/auth/me`, updated `getDashboardData()` to accept crop param

### New Files

1. **`backend/migrations/add_crop_location.sql`** - SQL migration script
2. **`backend/test_scripts/test_db_profile_flow.py`** - End-to-end test script

---

## 🗄️ SQL Migration

Run these commands in your PostgreSQL database:

```sql
-- Connect to your database
\c agrisense_db

-- Add crop column
ALTER TABLE users ADD COLUMN IF NOT EXISTS crop VARCHAR;

-- Add location column
ALTER TABLE users ADD COLUMN IF NOT EXISTS location VARCHAR;

-- Verify columns were added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('crop', 'location');
```

**Alternative: Using psql command line:**

```bash
psql -U postgres -d agrisense_db -f backend/migrations/add_crop_location.sql
```

---

## 🧪 Testing

### 1. Run Database Migration

```bash
# Connect to PostgreSQL
psql -U postgres -d agrisense_db

# Run migration
\i backend/migrations/add_crop_location.sql

# Or copy-paste the ALTER TABLE commands directly
```

### 2. Test Backend Endpoints

```bash
cd agrisense/backend

# Start backend server
uvicorn app.main:app --reload

# In another terminal, run test script
python test_scripts/test_db_profile_flow.py
```

### 3. Test Frontend

```bash
cd agrisense

# Start frontend
npm run dev

# Visit:
# - http://localhost:5173/profile (update crop & location)
# - http://localhost:5173/dashboard (should highlight your crop)
# - http://localhost:5173/advisory (should default to your crop)
```

---

## 📝 Code Changes Summary

### Backend Changes

#### `backend/app/models.py`
- Added `crop` and `location` columns to User model
- Added `phone` and `user_type` columns (if missing)

#### `backend/app/schemas.py`
- Added `crop` and `location` to `UserCreate`
- Added `UserUpdate` schema for profile updates
- Added `crop` and `location` to `UserOut`

#### `backend/app/crud.py`
- Updated `create_user()` to save crop and location
- Added `update_user()` function for profile updates

#### `backend/app/auth.py`
- Updated `signup()` to return crop and location
- Updated `login()` to return crop and location
- Updated `/auth/me` to return crop and location
- Added `PATCH /auth/profile` endpoint

#### `backend/app/fusion_engine.py`
- Added optional `crop` query parameter to `/fusion/dashboard`
- Returns `user_crop` in response if provided

#### `backend/app/main.py`
- Replaced in-memory endpoints with auth router
- Added database table creation on startup

### Frontend Changes

#### `src/pages/Profile.tsx`
- Added crop dropdown (cotton, wheat, rice, sugarcane, soybean, onion)
- Added location input with geolocate button
- Implemented `updateProfile()` API call
- Removed unused fields (region, farmSize, address)

#### `src/pages/Dashboard.tsx`
- Loads user profile on mount
- Passes user's crop to `/fusion/dashboard?crop={crop}`
- Highlights user's crop card with ring border and "(Your Crop)" label

#### `src/pages/Advisory.tsx`
- Defaults to user's crop if no URL parameter
- Loads user profile on mount when no crop param

#### `src/services/api.ts`
- Added `UserUpdate` interface
- Updated `User` interface with `crop` and `location`
- Added `updateProfile()` function
- Updated `getCurrentUser()` to use `/auth/me` endpoint
- Updated `getDashboardData()` to accept optional crop parameter

---

## 🚀 Quick Start Checklist

### 1. Database Setup

```bash
# Connect to PostgreSQL
psql -U postgres -d agrisense_db

# Run migration
ALTER TABLE users ADD COLUMN IF NOT EXISTS crop VARCHAR;
ALTER TABLE users ADD COLUMN IF NOT EXISTS location VARCHAR;
```

### 2. Backend Setup

```bash
cd agrisense/backend

# Activate virtual environment (if using)
# Windows:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd agrisense

# Install dependencies (if needed)
npm install

# Start dev server
npm run dev
```

### 4. Test Flow

1. **Sign up** at `http://localhost:5173/signup` (crop/location optional)
2. **Update profile** at `http://localhost:5173/profile`:
   - Select crop from dropdown
   - Enter location (or use geolocate button)
   - Click "Save Changes"
3. **View dashboard** at `http://localhost:5173/dashboard`:
   - Your crop card should be highlighted
   - Dashboard API called with `?crop={your_crop}`
4. **View advisory** at `http://localhost:5173/advisory`:
   - Should default to your crop
   - Can change via dropdown

---

## 🧪 Test Script Usage

```bash
cd agrisense/backend

# Make sure backend is running first!
uvicorn app.main:app --reload

# In another terminal:
python test_scripts/test_db_profile_flow.py
```

**Expected Output:**
- ✅ User created with crop and location
- ✅ Login successful
- ✅ Profile retrieved with crop/location
- ✅ Profile updated successfully
- ✅ Dashboard with crop param works
- ✅ Advisory for user's crop works

---

## 📊 API Endpoints

### New/Updated Endpoints

1. **`PATCH /auth/profile`** (NEW)
   - Requires: `Authorization: Bearer <token>`
   - Body: `{ "crop": "cotton", "location": "Punjab, India" }`
   - Returns: Updated user object

2. **`GET /auth/me`** (UPDATED)
   - Requires: `Authorization: Bearer <token>`
   - Returns: User object with crop and location

3. **`GET /fusion/dashboard?crop={crop}`** (UPDATED)
   - Optional query param: `crop`
   - Returns: Dashboard data with `user_crop` field if provided

4. **`POST /auth/signup`** (UPDATED)
   - Body can include: `crop`, `location` (optional)
   - Returns: User object with crop and location

5. **`POST /auth/login`** (UPDATED)
   - Returns: User object with crop and location

---

## ✅ Verification Checklist

- [ ] SQL migration executed successfully
- [ ] Backend server starts without errors
- [ ] Test script passes all tests
- [ ] Frontend Profile page shows crop dropdown and location input
- [ ] Profile update saves to database
- [ ] Dashboard highlights user's crop card
- [ ] Advisory defaults to user's crop
- [ ] All existing functionality still works

---

## 🐛 Troubleshooting

### Database Errors

**Error: `column "crop" does not exist`**
- Solution: Run SQL migration commands

**Error: `relation "users" does not exist`**
- Solution: Tables are auto-created on startup. Check `backend/app/main.py` has `Base.metadata.create_all(bind=engine)`

### Backend Errors

**Error: `ModuleNotFoundError: No module named 'app'`**
- Solution: Run from `backend/` directory: `uvicorn app.main:app --reload`

**Error: `AttributeError: 'User' object has no attribute 'crop'`**
- Solution: Restart backend server after running migration

### Frontend Errors

**Error: `401 Unauthorized` on `/auth/me`**
- Solution: Make sure user is logged in and token is valid

**Error: `Crop not showing in dashboard`**
- Solution: Check browser console, verify user.crop is set in profile

---

## 📦 Summary

All code changes have been implemented. The system now:

1. ✅ Stores user crop and location in PostgreSQL
2. ✅ Allows profile updates via PATCH endpoint
3. ✅ Passes user's crop to fusion dashboard
4. ✅ Highlights user's crop in dashboard
5. ✅ Defaults advisory to user's crop
6. ✅ Provides geolocation fallback for location input

**No UI layout changes** - only added fields and functionality while maintaining existing design.


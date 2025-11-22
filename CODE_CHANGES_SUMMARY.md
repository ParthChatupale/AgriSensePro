# Code Changes Summary - User Crop & Location Integration

## 📁 Backend Changes

### 1. `backend/app/models.py`

**Added fields to User model:**

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    user_type = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    crop = Column(String, nullable=True)  # Primary crop (cotton, wheat, rice, etc.)
    location = Column(String, nullable=True)  # Farm location
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### 2. `backend/app/schemas.py`

**Added UserUpdate schema and updated existing schemas:**

```python
class UserCreate(UserBase):
    password: str
    phone: Optional[str] = None
    userType: str = Field(alias="userType")
    crop: Optional[str] = None
    location: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    crop: Optional[str] = None
    location: Optional[str] = None

class UserOut(UserBase):
    id: int
    phone: Optional[str] = None
    userType: Optional[str] = None
    crop: Optional[str] = None
    location: Optional[str] = None
    is_active: bool
```

### 3. `backend/app/crud.py`

**Updated create_user and added update_user:**

```python
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        name=user.name,
        phone=user.phone,
        user_type=user.userType,
        crop=user.crop,
        location=user.location,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    """Update user profile fields."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user
```

### 4. `backend/app/auth.py`

**Added PATCH /auth/profile endpoint and updated existing endpoints:**

```python
@router.post("/signup")
async def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # ... existing code ...
    user = crud.create_user(db, user_in)
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "userType": user.user_type,
        "crop": user.crop,
        "location": user.location,
        "is_active": user.is_active,
    }

@router.post("/login")
async def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    # ... existing code ...
    return {"access_token": access_token, "token_type": "bearer", "user": {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "userType": user.user_type,
        "crop": user.crop,
        "location": user.location,
        "is_active": user.is_active,
    }}

@router.get("/me")
async def me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "phone": current_user.phone,
        "userType": current_user.user_type,
        "crop": current_user.crop,
        "location": current_user.location,
        "is_active": current_user.is_active,
    }

@router.patch("/profile", response_model=schemas.UserOut)
async def update_profile(
    user_update: schemas.UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""
    updated_user = crud.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": updated_user.id,
        "email": updated_user.email,
        "name": updated_user.name,
        "phone": updated_user.phone,
        "userType": updated_user.user_type,
        "crop": updated_user.crop,
        "location": updated_user.location,
        "is_active": updated_user.is_active,
    }
```

### 5. `backend/app/fusion_engine.py`

**Updated dashboard endpoint to accept crop query param:**

```python
@router.get("/dashboard")
async def get_dashboard_data(crop: str = None):
    # ... existing code ...
    response_data = {
        "weather": weather,
        "market": market,
        "alerts": alerts,
        "crop_health": crop_health,
        "summary": {...},
        "timestamp": weather.get("timestamp", "2025-11-10T16:00:00Z")
    }
    
    # Add user's crop if provided
    if crop:
        response_data["user_crop"] = crop.lower()
    
    return JSONResponse(response_data)
```

### 6. `backend/app/main.py`

**Replaced in-memory endpoints with auth router:**

```python
from .database import Base, engine
from . import fusion_engine, auth

# Create database tables
Base.metadata.create_all(bind=engine)

# ... CORS middleware ...

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(fusion_engine.router)
```

---

## 📁 Frontend Changes

### 1. `src/services/api.ts`

**Added UserUpdate interface and updateProfile function:**

```typescript
export interface User {
  name: string;
  email: string;
  phone?: string;
  userType: string;
  crop?: string;
  location?: string;
}

export interface UserUpdate {
  name?: string;
  phone?: string;
  crop?: string;
  location?: string;
}

export const getCurrentUser = async (): Promise<User> => {
  try {
    const response = await api.get<User>("/auth/me");
    if (response.data) {
      localStorage.setItem("user_data", JSON.stringify(response.data));
    }
    return response.data;
  } catch (error: any) {
    // ... error handling ...
  }
};

export const updateProfile = async (userData: UserUpdate): Promise<User> => {
  try {
    const response = await api.patch<User>("/auth/profile", userData);
    if (response.data) {
      localStorage.setItem("user_data", JSON.stringify(response.data));
    }
    return response.data;
  } catch (error: any) {
    // ... error handling ...
  }
};

export const getDashboardData = async (crop?: string): Promise<DashboardResponse> => {
  try {
    const url = crop ? `/fusion/dashboard?crop=${encodeURIComponent(crop)}` : "/fusion/dashboard";
    const response = await api.get<DashboardResponse>(url);
    return response.data;
  } catch (error: any) {
    // ... error handling ...
  }
};
```

### 2. `src/pages/Profile.tsx`

**Key changes:**
- Added crop dropdown with 6 options
- Added location input with geolocate button
- Implemented `updateProfile()` API call
- Removed unused fields (region, farmSize, address)

**Crop dropdown:**
```typescript
<Select
  value={formData.crop}
  onValueChange={(value) => setFormData({ ...formData, crop: value })}
>
  <SelectTrigger id="crop">
    <SelectValue placeholder="Select primary crop" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="cotton">Cotton</SelectItem>
    <SelectItem value="wheat">Wheat</SelectItem>
    <SelectItem value="rice">Rice</SelectItem>
    <SelectItem value="sugarcane">Sugarcane</SelectItem>
    <SelectItem value="soybean">Soybean</SelectItem>
    <SelectItem value="onion">Onion</SelectItem>
  </SelectContent>
</Select>
```

**Location input with geolocate:**
```typescript
<div className="flex gap-2">
  <Input 
    id="location" 
    value={formData.location}
    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
    placeholder="Enter farm location or coordinates"
  />
  <Button
    type="button"
    variant="outline"
    size="icon"
    onClick={handleGeolocate}
    title="Auto-detect location"
  >
    <MapPin className="h-4 w-4" />
  </Button>
</div>
```

### 3. `src/pages/Dashboard.tsx`

**Key changes:**
- Loads user profile on mount
- Passes user's crop to dashboard API
- Highlights user's crop card

```typescript
const [userCrop, setUserCrop] = useState<string | null>(null);

useEffect(() => {
  const loadUserProfile = async () => {
    try {
      const user = await getCurrentUser();
      if (user.crop) {
        setUserCrop(user.crop);
      }
    } catch (err) {
      console.log("Could not load user profile");
    }
  };
  loadUserProfile();
}, []);

const fetchDashboardData = async () => {
  // ...
  const data = await getDashboardData(userCrop || undefined);
  // ...
};

// In crop health cards:
const isUserCrop = userCrop && cropName.toLowerCase() === userCrop.toLowerCase();
<Card className={`p-4 ${isUserCrop ? "ring-2 ring-primary" : ""}`}>
  {isUserCrop && <span className="text-xs text-primary">(Your Crop)</span>}
</Card>
```

### 4. `src/pages/Advisory.tsx`

**Key changes:**
- Defaults to user's crop if no URL param

```typescript
useEffect(() => {
  const loadUserCrop = async () => {
    if (!cropParam) {
      try {
        const user = await getCurrentUser();
        if (user.crop) {
          setSelectedCrop(user.crop);
        }
      } catch (err) {
        // Silently fail - default to cotton
      }
    }
  };
  loadUserCrop();
}, [cropParam]);
```

---

## 🗄️ SQL Migration

**File: `backend/migrations/add_crop_location.sql`**

```sql
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

---

## 🧪 Test Script

**File: `backend/test_scripts/test_db_profile_flow.py`**

Tests:
1. Signup with crop and location
2. Login and get token
3. Get current user profile
4. Update profile (crop and location)
5. Fetch dashboard with crop param
6. Fetch advisory for user's crop

---

## ✅ Quick Start Commands

```bash
# 1. Database Migration
psql -U postgres -d agrisense_db
ALTER TABLE users ADD COLUMN IF NOT EXISTS crop VARCHAR;
ALTER TABLE users ADD COLUMN IF NOT EXISTS location VARCHAR;
\q

# 2. Backend
cd agrisense/backend
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac
uvicorn app.main:app --reload

# 3. Frontend
cd agrisense
npm run dev

# 4. Test
cd agrisense/backend
python test_scripts/test_db_profile_flow.py
```

---

## 📊 API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Signup (crop, location optional) |
| POST | `/auth/login` | Login (returns crop, location) |
| GET | `/auth/me` | Get current user (returns crop, location) |
| PATCH | `/auth/profile` | Update profile (crop, location) |
| GET | `/fusion/dashboard?crop={crop}` | Dashboard with crop filter |
| GET | `/fusion/advisory/{crop}` | Advisory for crop |

---

All changes maintain existing UI layout and only add functionality.


from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from . import fusion_engine, auth, community, ai
from .routes import advisory_pdf
from .agmarknet.api import dashboard as agmarknet_dashboard
from .agmarknet.api import metadata as agmarknet_metadata
from ndvi.ndvi_router import router as ndvi_image_router  # Image generation router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="krushiRakshak Backend API",
    description="Backend API for krushiRakshak PWA — Farmer advisory and risk management system",
    version="1.0.0",
)

# -------------------------------------------------------------------
# ✅ Enable CORS (important for frontend-backend communication)
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# 🔌 Include routers
# -------------------------------------------------------------------
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(fusion_engine.router)
app.include_router(community.router)
app.include_router(ai.router)
app.include_router(advisory_pdf.router)
app.include_router(agmarknet_dashboard.router)
app.include_router(agmarknet_metadata.router)
# Expose NDVI image generation under /api/ndvi/run
app.include_router(ndvi_image_router, prefix="/api/ndvi", tags=["ndvi"])

# -------------------------------------------------------------------
# 🌐 Root Route
# -------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to krushiRakshak Backend API"}


# -------------------------------------------------------------------
# ⚙️ To Run the Server:
# -------------------------------------------------------------------
# Open terminal inside backend folder and run:
# uvicorn main:app --reload
#
# Then visit http://127.0.0.1:8000/docs to test APIs interactively.

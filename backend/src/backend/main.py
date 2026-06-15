# backend/src/main.py
from fastapi import FastAPI
# backend/src/main.py
from backend.db.db import Base, engine
from backend.api import candidate, interview
from fastapi.middleware.cors import CORSMiddleware

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],            # allow all HTTP methods
    allow_headers=["*"],            # allow all headers
)

# Create tables
Base.metadata.create_all(bind=engine)


# Mount routers
app.include_router(candidate.router, prefix="/candidate", tags=["candidate"])
app.include_router(interview.router, prefix="/interview", tags=["interview"])

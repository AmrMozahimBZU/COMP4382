from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import applications, applicants, staff

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="LRMIS - Land Registration Management Information System",
    description="Advanced geo-enabled platform for land registration services",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router, prefix="/applications", tags=["Applications"])
app.include_router(applicants.router, prefix="/applicants", tags=["Applicants"])
app.include_router(staff.router, prefix="/staff", tags=["Staff"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to LRMIS API", "docs": "/docs"}

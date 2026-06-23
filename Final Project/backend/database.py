import motor.motor_asyncio
from beanie import init_beanie
from config import settings
from models import LandApplication, Applicant, StaffMember, Parcel, Certificate, Objection, ApplicationDocument, PerformanceLog, SurveyTask

async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.DB_URL)
    db = client[settings.DB_NAME]

    # Create 2dsphere index for geospatial queries
    await db["parcels"].create_index([("location", "2dsphere")])

    await init_beanie(
        database=db,
        document_models=[
            LandApplication,
            Applicant,
            StaffMember,
            Parcel,
            Certificate,
            Objection,
            ApplicationDocument,
            PerformanceLog,
            SurveyTask,
        ]
    )

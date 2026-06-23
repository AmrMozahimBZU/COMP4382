from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from models import Applicant, LandApplication, CreateApplicant, VerificationState

router = APIRouter()


# ── POST /applicants/ ────────────────────────
@router.post("/", status_code=201)
async def create_applicant(data: CreateApplicant):
    existing = await Applicant.find_one(Applicant.national_id == data.national_id)
    if existing:
        raise HTTPException(status_code=409, detail="Applicant with this national ID already exists")
    applicant = Applicant(**data.model_dump())
    await applicant.insert()
    return applicant


# ── GET /applicants/ ─────────────────────────
@router.get("/")
async def list_applicants():
    return await Applicant.find_all().to_list()


# ── GET /applicants/{id} ─────────────────────
@router.get("/{applicant_id}")
async def get_applicant(applicant_id: PydanticObjectId):
    applicant = await Applicant.get(applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    # Restrict sensitive fields
    result = applicant.model_dump()
    if applicant.privacy_settings.get("show_contact") is False:
        result.pop("email", None)
        result.pop("phone", None)
    return result


# ── GET /applicants/{id}/applications ────────
@router.get("/{applicant_id}/applications")
async def get_applicant_applications(applicant_id: PydanticObjectId):
    applicant = await Applicant.get(applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    apps = await LandApplication.find(LandApplication.applicant_id == str(applicant_id)).to_list()
    return {"applicant": applicant.full_name, "applications": apps}


# ── PATCH /applicants/{id}/verify ────────────
@router.patch("/{applicant_id}/verify")
async def verify_applicant(applicant_id: PydanticObjectId, state: str = "verified"):
    applicant = await Applicant.get(applicant_id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    try:
        applicant.verification_state = VerificationState(state)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid state: {state}")
    await applicant.save()
    return applicant

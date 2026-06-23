from fastapi import APIRouter, HTTPException, Body
from beanie import PydanticObjectId
from typing import Optional
from datetime import datetime

from models import (
    StaffMember, SurveyTask, LandApplication,
    CreateStaff, UpdateSurveyMilestone, UploadSurveyReport,
    StaffRole, SurveyMilestone, ApplicationStatus
)

router = APIRouter()


# ── POST /staff/ ─────────────────────────────
@router.post("/", status_code=201)
async def create_staff(data: CreateStaff):
    existing = await StaffMember.find_one(StaffMember.national_id == data.national_id)
    if existing:
        raise HTTPException(status_code=409, detail="Staff member with this national ID already exists")
    staff = StaffMember(**data.model_dump())
    await staff.insert()
    return staff


# ── GET /staff/ ───────────────────────────────
@router.get("/")
async def list_staff(role: Optional[str] = None):
    if role:
        try:
            r = StaffRole(role)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
        return await StaffMember.find(StaffMember.role == r).to_list()
    return await StaffMember.find_all().to_list()


# ── GET /staff/{id} ───────────────────────────
@router.get("/{staff_id}")
async def get_staff(staff_id: PydanticObjectId):
    staff = await StaffMember.get(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    tasks = await SurveyTask.find(SurveyTask.surveyor_id == str(staff_id)).to_list()
    completed = [t for t in tasks if t.milestone == SurveyMilestone.registrar_reviewed]

    return {
        "staff": staff,
        "workload": staff.current_workload,
        "total_tasks": len(tasks),
        "completed_tasks": len(completed),
        "active_tasks": tasks
    }


# ── PATCH /staff/{id}/availability ───────────
@router.patch("/{staff_id}/availability")
async def update_availability(staff_id: PydanticObjectId, available: bool = Body(..., embed=True)):
    staff = await StaffMember.get(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    staff.availability = available
    await staff.save()
    return {"message": f"Availability set to {available}", "staff": staff}


# ── GET /staff/{id}/tasks ─────────────────────
@router.get("/{staff_id}/tasks")
async def get_staff_tasks(staff_id: PydanticObjectId):
    tasks = await SurveyTask.find(SurveyTask.surveyor_id == str(staff_id)).to_list()
    return {"surveyor_id": str(staff_id), "tasks": tasks}


# ── PATCH /staff/tasks/{task_id}/milestone ────
@router.patch("/tasks/{task_id}/milestone")
async def update_task_milestone(task_id: PydanticObjectId, data: UpdateSurveyMilestone):
    task = await SurveyTask.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Survey task not found")

    task.milestone = data.milestone
    task.updated_at = datetime.now()
    task.milestone_history.append({
        "milestone": data.milestone.value,
        "timestamp": datetime.now().isoformat(),
        "note": data.note or ""
    })
    await task.save()

    # If report uploaded, reflect on application
    if data.milestone == SurveyMilestone.report_uploaded:
        app = await LandApplication.get(PydanticObjectId(task.application_id))
        if app:
            app.status = ApplicationStatus.surveyed
            app.updated_at = datetime.now()
            app.status_history.append({"status": "surveyed", "timestamp": datetime.now().isoformat(), "note": "Survey report uploaded by surveyor"})
            await app.save()

    return task


# ── POST /staff/tasks/{task_id}/report ────────
@router.post("/tasks/{task_id}/report")
async def upload_task_report(task_id: PydanticObjectId, data: UploadSurveyReport):
    task = await SurveyTask.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Survey task not found")

    task.report_metadata = {
        "title": data.report_title,
        "findings": data.findings,
        "recommendations": data.recommendations,
        "uploaded_at": datetime.now().isoformat()
    }
    task.milestone = SurveyMilestone.report_uploaded
    task.updated_at = datetime.now()
    task.milestone_history.append({"milestone": "report_uploaded", "timestamp": datetime.now().isoformat()})
    await task.save()

    # Update application
    app = await LandApplication.get(PydanticObjectId(task.application_id))
    if app:
        app.survey_report = task.report_metadata
        app.status = ApplicationStatus.surveyed
        app.updated_at = datetime.now()
        app.status_history.append({"status": "surveyed", "timestamp": datetime.now().isoformat(), "note": "Report uploaded"})
        await app.save()

    return {"message": "Report uploaded", "task": task}


# ── GET /staff/registrar/review-queue ─────────
@router.get("/registrar/review-queue")
async def registrar_review_queue():
    """Applications pending legal review"""
    apps = await LandApplication.find(
        LandApplication.status == ApplicationStatus.legal_review
    ).to_list()
    return {"pending_legal_review": len(apps), "applications": apps}


# ── PATCH /staff/registrar/{app_id}/decision ──
@router.patch("/registrar/{application_id}/decision")
async def registrar_decision(
    application_id: PydanticObjectId,
    decision: str = Body(..., embed=True),
    remarks: str = Body(..., embed=True)
):
    """Registrar approves or rejects after legal review"""
    app = await LandApplication.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.status != ApplicationStatus.legal_review:
        raise HTTPException(status_code=400, detail="Application must be in legal_review status")

    app.registrar_remarks = remarks
    if decision == "approve":
        app.status = ApplicationStatus.approved
    elif decision == "reject":
        app.status = ApplicationStatus.rejected
        app.rejection_reason = remarks
    else:
        raise HTTPException(status_code=400, detail="Decision must be 'approve' or 'reject'")

    app.updated_at = datetime.now()
    app.status_history.append({"status": app.status.value, "timestamp": datetime.now().isoformat(), "note": remarks})
    await app.save()
    return app

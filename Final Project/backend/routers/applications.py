from fastapi import APIRouter, HTTPException, Query
from beanie import PydanticObjectId
from typing import Optional, List
from datetime import datetime
import uuid

from models import (
    LandApplication, Certificate, PerformanceLog, SurveyTask,
    Objection, ApplicationDocument,
    CreateApplication, TransitionApplication, HoldApplication,
    RejectApplication, AddDocument, AddComment, SubmitObjection,
    ApplicationStatus, SurveyMilestone
)

router = APIRouter()

# ── Valid state transitions ──────────────────
VALID_TRANSITIONS = {
    ApplicationStatus.submitted: [ApplicationStatus.pre_checked, ApplicationStatus.missing_documents, ApplicationStatus.rejected],
    ApplicationStatus.pre_checked: [ApplicationStatus.survey_required, ApplicationStatus.legal_review, ApplicationStatus.missing_documents],
    ApplicationStatus.survey_required: [ApplicationStatus.surveyed, ApplicationStatus.on_hold],
    ApplicationStatus.surveyed: [ApplicationStatus.legal_review],
    ApplicationStatus.legal_review: [ApplicationStatus.approved, ApplicationStatus.rejected, ApplicationStatus.under_objection],
    ApplicationStatus.approved: [ApplicationStatus.certificate_issued],
    ApplicationStatus.certificate_issued: [ApplicationStatus.closed],
    ApplicationStatus.missing_documents: [ApplicationStatus.pre_checked, ApplicationStatus.rejected],
    ApplicationStatus.under_objection: [ApplicationStatus.legal_review, ApplicationStatus.rejected, ApplicationStatus.on_hold],
    ApplicationStatus.on_hold: [ApplicationStatus.survey_required, ApplicationStatus.legal_review, ApplicationStatus.rejected],
}

async def log_event(entity_type: str, entity_id: str, event: str, details=None):
    log = PerformanceLog(entity_type=entity_type, entity_id=entity_id, event=event, details=details)
    await log.insert()


# ── POST /applications/ ──────────────────────
@router.post("/", status_code=201)
async def create_application(data: CreateApplication):
    # Idempotency check
    if data.idempotency_key:
        existing = await LandApplication.find_one(LandApplication.idempotency_key == data.idempotency_key)
        if existing:
            return existing

    app = LandApplication(**data.model_dump())
    app.status_history.append({"status": "submitted", "timestamp": datetime.now().isoformat(), "note": "Application submitted"})
    await app.insert()
    await log_event("application", str(app.id), "created", {"type": data.application_type})
    return app


# ── GET /applications/ ──────────────────────
@router.get("/")
async def list_applications(
    status: Optional[str] = Query(None),
    application_type: Optional[str] = Query(None),
    zone: Optional[str] = Query(None),
    applicant_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    sort_by: str = Query("submitted_at"),
):
    query = {}
    if status:
        query["status"] = status
    if application_type:
        query["application_type"] = application_type
    if zone:
        query["zone"] = zone
    if applicant_id:
        query["applicant_id"] = applicant_id

    apps = await LandApplication.find(query).skip(skip).limit(limit).to_list()
    return {"total": len(apps), "results": apps}


# ── GET /applications/{id} ──────────────────
@router.get("/{application_id}")
async def get_application(application_id: PydanticObjectId):
    app = await LandApplication.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


# ── PATCH /applications/{id}/transition ─────
@router.patch("/{application_id}/transition")
async def transition_application(application_id: PydanticObjectId, data: TransitionApplication):
    app = await LandApplication.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    allowed = VALID_TRANSITIONS.get(app.status, [])
    if data.new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from '{app.status}' to '{data.new_status}'. Allowed: {[s.value for s in allowed]}"
        )

    # Transition guards
    if data.new_status == ApplicationStatus.pre_checked:
        if not app.applicant_name or not app.parcel_number:
            raise HTTPException(status_code=400, detail="Applicant name and parcel number required for pre_checked")

    if data.new_status == ApplicationStatus.survey_required:
        if not app.parcel_location:
            raise HTTPException(status_code=400, detail="Parcel location (GeoJSON) required before survey_required")

    if data.new_status == ApplicationStatus.surveyed:
        if not app.survey_report:
            raise HTTPException(status_code=400, detail="Survey report must exist before marking as surveyed")

    if data.new_status == ApplicationStatus.legal_review:
        if not app.documents:
            raise HTTPException(status_code=400, detail="Ownership documents must be uploaded before legal review")

    if data.new_status == ApplicationStatus.approved:
        if not app.registrar_remarks:
            raise HTTPException(status_code=400, detail="Registrar must add remarks before approving")

    # Handle objection auto-move
    if data.new_status == ApplicationStatus.under_objection:
        app.status = ApplicationStatus.under_objection
    else:
        app.status = data.new_status

    app.updated_at = datetime.now()
    app.status_history.append({
        "status": data.new_status.value,
        "timestamp": datetime.now().isoformat(),
        "note": data.note or ""
    })
    await app.save()
    await log_event("application", str(app.id), "transition", {"new_status": data.new_status})
    return app


# ── POST /applications/{id}/hold ─────────────
@router.post("/{application_id}/hold")
async def hold_application(application_id: PydanticObjectId, data: HoldApplication):
    app = await LandApplication.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = ApplicationStatus.on_hold
    app.hold_reason = data.reason
    app.updated_at = datetime.now()
    app.status_history.append({"status": "on_hold", "timestamp": datetime.now().isoformat(), "note": data.reason})
    await app.save()
    return app


# ── POST /applications/{id}/reject ───────────
@router.post("/{application_id}/reject")
async def reject_application(application_id: PydanticObjectId, data: RejectApplication):
    app = await LandApplication.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = ApplicationStatus.rejected
    app.rejection_reason = data.reason
    app.updated_at = datetime.now()
    app.status_history.append({"status": "rejected", "timestamp": datetime.now().isoformat(), "note": data.reason})
    await app.save()
    await log_event("application", str(app.id), "rejected", {"reason": data.reason})
    return app


# ── POST /applications/{id}/certificate ──────
@router.post("/{application_id}/certificate")
async def issue_certificate(application_id: PydanticObjectId):
    app = await LandApplication.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.status != ApplicationStatus.approved:
        raise HTTPException(status_code=400, detail="Application must be approved before issuing certificate")

    cert_number = f"CERT-{uuid.uuid4().hex[:8].upper()}"
    cert = Certificate(
        application_id=str(app.id),
        applicant_id=app.applicant_id,
        parcel_number=app.parcel_number,
        certificate_number=cert_number,
        qr_code_stub=f"https://lrmis.gov/verify/{cert_number}"
    )
    await cert.insert()

    app.certificate_id = str(cert.id)
    app.status = ApplicationStatus.certificate_issued
    app.updated_at = datetime.now()
    app.status_history.append({"status": "certificate_issued", "timestamp": datetime.now().isoformat(), "note": cert_number})
    await app.save()
    await log_event("application", str(app.id), "certificate_issued", {"cert_number": cert_number})
    return cert


# ── GET /applications/{id}/timeline ──────────
@router.get("/{application_id}/timeline")
async def get_timeline(application_id: PydanticObjectId):
    app = await LandApplication.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"application_id": str(app.id), "status": app.status, "timeline": app.status_history}


# ── POST /applications/{id}/documents ────────
@router.post("/{application_id}/documents")
async def add_document(application_id: PydanticObjectId, data: AddDocument):
    app = await LandApplication.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    doc_entry = {"type": data.document_type, "file_name": data.file_name, "file_url": data.file_url, "verified": False, "uploaded_at": datetime.now().isoformat()}
    app.documents.append(doc_entry)
    app.updated_at = datetime.now()
    await app.save()

    doc = ApplicationDocument(
        application_id=str(application_id),
        applicant_id=data.applicant_id,
        document_type=data.document_type,
        file_name=data.file_name,
        file_url=data.file_url
    )
    await doc.insert()
    return {"message": "Document added", "document": doc_entry}


# ── POST /applications/{id}/comments ─────────
@router.post("/{application_id}/comments")
async def add_comment(application_id: PydanticObjectId, data: AddComment):
    app = await LandApplication.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    note = {"by": data.applicant_id or "applicant", "comment": data.comment, "timestamp": datetime.now().isoformat()}
    app.internal_notes.append(note)
    await app.save()
    return {"message": "Comment added", "note": note}


# ── POST /applications/{id}/objections ───────
@router.post("/{application_id}/objections")
async def submit_objection(application_id: PydanticObjectId, data: SubmitObjection):
    app = await LandApplication.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    obj = Objection(
        application_id=str(application_id),
        applicant_id=data.applicant_id,
        reason=data.reason,
        supporting_documents=data.supporting_documents
    )
    await obj.insert()

    app.status = ApplicationStatus.under_objection
    app.updated_at = datetime.now()
    app.status_history.append({"status": "under_objection", "timestamp": datetime.now().isoformat(), "note": "Objection submitted"})
    await app.save()
    return obj


# ── POST /applications/{id}/auto-assign-surveyor ─
@router.post("/{application_id}/auto-assign-surveyor")
async def auto_assign_surveyor(application_id: PydanticObjectId):
    from models import StaffMember, StaffRole
    app = await LandApplication.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Find best surveyor: zone match + available + lowest workload
    surveyors = await StaffMember.find(
        StaffMember.role == StaffRole.surveyor,
        StaffMember.availability == True
    ).to_list()

    if not surveyors:
        raise HTTPException(status_code=404, detail="No available surveyors")

    # Zone match first, then lowest workload
    zone_matched = [s for s in surveyors if app.zone in s.coverage_zones] if app.zone else surveyors
    candidates = zone_matched if zone_matched else surveyors
    best = min(candidates, key=lambda s: s.current_workload)

    task = SurveyTask(
        application_id=str(application_id),
        surveyor_id=str(best.id),
        parcel_number=app.parcel_number,
        zone=app.zone,
        priority=2
    )
    await task.insert()

    best.current_workload += 1
    await best.save()

    app.survey_task_id = str(task.id)
    app.status = ApplicationStatus.survey_required
    app.updated_at = datetime.now()
    app.status_history.append({"status": "survey_required", "timestamp": datetime.now().isoformat(), "note": f"Assigned to {best.full_name}"})
    await app.save()

    return {"message": f"Assigned to {best.full_name}", "task": task}


# ── PATCH /applications/{id}/survey-milestone ─
@router.patch("/{application_id}/survey-milestone")
async def update_survey_milestone(application_id: PydanticObjectId, data):
    from models import UpdateSurveyMilestone
    task = await SurveyTask.find_one(SurveyTask.application_id == str(application_id))
    if not task:
        raise HTTPException(status_code=404, detail="Survey task not found")
    task.milestone = data.milestone
    task.updated_at = datetime.now()
    task.milestone_history.append({"milestone": data.milestone, "timestamp": datetime.now().isoformat(), "note": data.note or ""})
    await task.save()
    return task


# ── POST /applications/{id}/survey-report ────
@router.post("/{application_id}/survey-report")
async def upload_survey_report(application_id: PydanticObjectId, data):
    from models import UploadSurveyReport
    app = await LandApplication.get(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    report = {
        "surveyor_id": data.surveyor_id,
        "title": data.report_title,
        "findings": data.findings,
        "recommendations": data.recommendations,
        "uploaded_at": datetime.now().isoformat()
    }
    app.survey_report = report
    app.status = ApplicationStatus.surveyed
    app.updated_at = datetime.now()
    app.status_history.append({"status": "surveyed", "timestamp": datetime.now().isoformat(), "note": "Survey report uploaded"})
    await app.save()
    return {"message": "Survey report uploaded", "report": report}


# ── GET /analytics/ ───────────────────────────
@router.get("/analytics/summary")
async def analytics_summary():
    total = await LandApplication.count()
    by_status = {}
    for status in ApplicationStatus:
        count = await LandApplication.find(LandApplication.status == status).count()
        if count > 0:
            by_status[status.value] = count

    by_type = {}
    from models import ApplicationType
    for atype in ApplicationType:
        count = await LandApplication.find(LandApplication.application_type == atype).count()
        if count > 0:
            by_type[atype.value] = count

    return {
        "total_applications": total,
        "by_status": by_status,
        "by_type": by_type,
    }

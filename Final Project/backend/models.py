from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class ApplicationStatus(str, Enum):
    submitted = "submitted"
    pre_checked = "pre_checked"
    survey_required = "survey_required"
    surveyed = "surveyed"
    legal_review = "legal_review"
    approved = "approved"
    certificate_issued = "certificate_issued"
    closed = "closed"
    rejected = "rejected"
    on_hold = "on_hold"
    missing_documents = "missing_documents"
    under_objection = "under_objection"

class ApplicationType(str, Enum):
    first_registration = "first_registration"
    ownership_transfer = "ownership_transfer"
    parcel_subdivision = "parcel_subdivision"
    parcel_merge = "parcel_merge"
    boundary_correction = "boundary_correction"
    certificate_request = "certificate_request"

class ApplicantType(str, Enum):
    citizen = "citizen"
    lawyer = "lawyer"
    company = "company"
    surveyor = "surveyor"
    representative = "authorized_representative"

class VerificationState(str, Enum):
    unverified = "unverified"
    verified = "verified"
    suspended = "suspended"

class StaffRole(str, Enum):
    surveyor = "surveyor"
    registrar = "registrar"
    manager = "manager"

class SurveyMilestone(str, Enum):
    assigned = "assigned"
    visit_scheduled = "visit_scheduled"
    arrived_on_site = "arrived_on_site"
    survey_started = "survey_started"
    survey_completed = "survey_completed"
    report_uploaded = "report_uploaded"
    registrar_reviewed = "registrar_reviewed"


# ─────────────────────────────────────────────
# GEOJSON
# ─────────────────────────────────────────────

class GeoJSONPoint(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]

class GeoJSONPolygon(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]]


# ─────────────────────────────────────────────
# MODULE 1 - LAND APPLICATION
# ─────────────────────────────────────────────

class Parcel(Document):
    parcel_number: str
    block_number: Optional[str] = None
    basin_number: Optional[str] = None
    zone: Optional[str] = None
    area_sqm: Optional[float] = None
    location: Optional[GeoJSONPoint] = None
    boundary: Optional[GeoJSONPolygon] = None
    owner_references: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "parcels"


class LandApplication(Document):
    application_type: ApplicationType
    status: ApplicationStatus = ApplicationStatus.submitted
    idempotency_key: Optional[str] = None

    # Applicant info
    applicant_id: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_national_id: Optional[str] = None

    # Parcel info
    parcel_number: Optional[str] = None
    block_number: Optional[str] = None
    basin_number: Optional[str] = None
    zone: Optional[str] = None
    parcel_location: Optional[GeoJSONPoint] = None

    # Documents & notes
    documents: List[Dict[str, Any]] = []
    missing_documents: List[str] = []
    internal_notes: List[Dict[str, Any]] = []
    registrar_remarks: Optional[str] = None
    rejection_reason: Optional[str] = None
    hold_reason: Optional[str] = None

    # Survey
    survey_task_id: Optional[str] = None
    survey_report: Optional[Dict[str, Any]] = None

    # Certificate
    certificate_id: Optional[str] = None

    # Timeline
    status_history: List[Dict[str, Any]] = []
    submitted_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "land_applications"


class Certificate(Document):
    application_id: str
    applicant_id: Optional[str] = None
    parcel_number: Optional[str] = None
    certificate_number: str
    issue_date: datetime = Field(default_factory=datetime.now)
    qr_code_stub: Optional[str] = None
    status: str = "issued"

    class Settings:
        name = "certificates"


class PerformanceLog(Document):
    entity_type: str  # application, staff, etc.
    entity_id: str
    event: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "performance_logs"


# ─────────────────────────────────────────────
# MODULE 2 - APPLICANT PORTAL
# ─────────────────────────────────────────────

class Applicant(Document):
    full_name: str
    national_id: str
    applicant_type: ApplicantType = ApplicantType.citizen
    verification_state: VerificationState = VerificationState.unverified

    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    preferred_language: str = "ar"
    notification_preferences: Dict[str, bool] = {"email": True, "sms": False}
    privacy_settings: Dict[str, bool] = {"show_contact": False}

    linked_applications: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "applicants"


class ApplicationDocument(Document):
    application_id: str
    applicant_id: Optional[str] = None
    document_type: str
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    verified: bool = False
    uploaded_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "application_documents"


class Objection(Document):
    application_id: str
    applicant_id: Optional[str] = None
    reason: str
    supporting_documents: List[str] = []
    status: str = "pending"  # pending, reviewed, resolved
    registrar_response: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "objections"


# ─────────────────────────────────────────────
# MODULE 3 - STAFF & SURVEY
# ─────────────────────────────────────────────

class StaffMember(Document):
    full_name: str
    national_id: str
    role: StaffRole
    email: Optional[str] = None
    phone: Optional[str] = None

    # Surveyor-specific
    coverage_zones: List[str] = []
    skills: List[str] = []
    availability: bool = True
    current_workload: int = 0  # number of active tasks

    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "staff"


class SurveyTask(Document):
    application_id: str
    surveyor_id: Optional[str] = None
    parcel_number: Optional[str] = None
    zone: Optional[str] = None
    priority: int = 1  # 1=low, 2=medium, 3=high
    milestone: SurveyMilestone = SurveyMilestone.assigned
    milestone_history: List[Dict[str, Any]] = []
    scheduled_date: Optional[datetime] = None
    field_notes: Optional[str] = None
    report_metadata: Optional[Dict[str, Any]] = None
    assigned_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "survey_tasks"


# ─────────────────────────────────────────────
# REQUEST / RESPONSE SCHEMAS
# ─────────────────────────────────────────────

class CreateApplication(BaseModel):
    application_type: ApplicationType
    applicant_id: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_national_id: Optional[str] = None
    parcel_number: Optional[str] = None
    block_number: Optional[str] = None
    basin_number: Optional[str] = None
    zone: Optional[str] = None
    parcel_location: Optional[GeoJSONPoint] = None
    idempotency_key: Optional[str] = None

class TransitionApplication(BaseModel):
    new_status: ApplicationStatus
    note: Optional[str] = None

class HoldApplication(BaseModel):
    reason: str

class RejectApplication(BaseModel):
    reason: str

class CreateApplicant(BaseModel):
    full_name: str
    national_id: str
    applicant_type: ApplicantType = ApplicantType.citizen
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    preferred_language: str = "ar"

class CreateStaff(BaseModel):
    full_name: str
    national_id: str
    role: StaffRole
    email: Optional[str] = None
    phone: Optional[str] = None
    coverage_zones: List[str] = []
    skills: List[str] = []

class AddDocument(BaseModel):
    document_type: str
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    applicant_id: Optional[str] = None

class AddComment(BaseModel):
    applicant_id: Optional[str] = None
    comment: str

class SubmitObjection(BaseModel):
    applicant_id: Optional[str] = None
    reason: str
    supporting_documents: List[str] = []

class UpdateSurveyMilestone(BaseModel):
    milestone: SurveyMilestone
    note: Optional[str] = None

class UploadSurveyReport(BaseModel):
    surveyor_id: str
    report_title: str
    findings: str
    recommendations: Optional[str] = None

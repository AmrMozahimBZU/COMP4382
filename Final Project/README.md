# LRMIS - Land Registration Management Information System
### COMP4382 Final Project

A full-stack land registration platform built with **FastAPI + MongoDB (PyMongo/Beanie)** backend and **Streamlit** frontend.

---

## Project Structure

```
lrmis/
├── backend/
│   ├── app.py               # FastAPI main app
│   ├── config.py            # Settings (.env)
│   ├── database.py          # MongoDB / Beanie init
│   ├── models.py            # All Pydantic + Beanie models
│   ├── requirements.txt
│   ├── .env                 # DB connection string
│   └── routers/
│       ├── applications.py  # Module 1: Land Application Management
│       ├── applicants.py    # Module 2: Applicant Portal
│       └── staff.py         # Module 3: Surveyors & Registrar
│
└── frontend/
    ├── app.py               # Streamlit main entry
    ├── api.py               # HTTP helper (calls backend)
    ├── requirements.txt
    └── pages/
        ├── applicant_dashboard.py
        ├── submit_application.py
        ├── track_application.py
        ├── upload_documents.py
        ├── submit_objection.py
        ├── applicant_profile.py
        ├── staff_dashboard.py
        ├── applications_table.py
        ├── application_details.py
        ├── registrar_review.py
        ├── issue_certificate.py
        ├── manage_applicants.py
        ├── surveyor_tasks.py
        ├── task_execution.py
        ├── live_map.py
        ├── analytics.py
        └── staff_management.py
```

---

## Setup & Run

### Prerequisites
- Python 3.10+
- MongoDB running locally on port 27017 (or MongoDB Atlas)

### 1. Start MongoDB
```bash
mongod --dbpath /data/db
```
Or use MongoDB Atlas and update `.env` with your connection string.

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```
API docs available at: http://localhost:8000/docs

### 3. Frontend
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```
Opens at: http://localhost:8501

---

## Modules

### Module 1 — Land Application Management (`routers/applications.py`)
- Full CRUD for land registration applications
- Strict workflow state machine: `submitted → pre_checked → survey_required → surveyed → legal_review → approved → certificate_issued → closed`
- Alternative states: `rejected`, `on_hold`, `missing_documents`, `under_objection`
- Transition guards (e.g. can't approve without registrar remarks)
- GeoJSON parcel location support
- Certificate issuance with unique certificate number + QR stub
- Audit log via `PerformanceLog`
- Analytics endpoint: `/applications/analytics/summary`

### Module 2 — Applicant Portal (`routers/applicants.py`)
- Create and manage applicant profiles
- Types: citizen, lawyer, company, surveyor, authorized_representative
- Verification states: unverified, verified, suspended
- Link applications to applicants
- Document upload, comments, objection submission

### Module 3 — Surveyors, Registrar & Assignment (`routers/staff.py`)
- Create surveyors and registrar staff
- Auto-assign surveyor based on: zone match → lowest workload
- Survey milestones: `assigned → visit_scheduled → arrived_on_site → survey_started → survey_completed → report_uploaded → registrar_reviewed`
- Registrar review queue and decision endpoint
- Staff workload tracking

### Shared — Geospatial & Analytics (Module 4)
- GeoJSON parcel locations with MongoDB 2dsphere index
- Live map (Leaflet via Folium) showing parcels colored by status
- Analytics dashboard: applications by status, type, surveyor workload

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /applications/ | Create application |
| GET | /applications/ | List with filters |
| GET | /applications/{id} | Full details |
| PATCH | /applications/{id}/transition | Workflow transition |
| POST | /applications/{id}/hold | Place on hold |
| POST | /applications/{id}/reject | Reject with reason |
| POST | /applications/{id}/certificate | Issue certificate |
| GET | /applications/{id}/timeline | Status history |
| POST | /applications/{id}/documents | Upload document |
| POST | /applications/{id}/comments | Add comment |
| POST | /applications/{id}/objections | Submit objection |
| POST | /applications/{id}/auto-assign-surveyor | Auto-assign |
| GET | /applications/analytics/summary | Analytics |
| POST | /applicants/ | Register applicant |
| GET | /applicants/{id} | Get profile |
| GET | /applicants/{id}/applications | Applicant's apps |
| PATCH | /applicants/{id}/verify | Verify applicant |
| POST | /staff/ | Add staff |
| GET | /staff/ | List staff |
| GET | /staff/{id} | Staff profile + workload |
| PATCH | /staff/{id}/availability | Set availability |
| GET | /staff/{id}/tasks | Staff's survey tasks |
| PATCH | /staff/tasks/{id}/milestone | Update milestone |
| POST | /staff/tasks/{id}/report | Upload survey report |
| GET | /staff/registrar/review-queue | Legal review queue |
| PATCH | /staff/registrar/{id}/decision | Approve/reject |

---

## Technology Stack
- **Backend:** FastAPI, Beanie (ODM), Motor (async MongoDB), Pydantic, Uvicorn
- **Database:** MongoDB with 2dsphere geospatial index
- **Frontend:** Streamlit, Folium (map), Pandas
- **Documentation:** Swagger UI at /docs

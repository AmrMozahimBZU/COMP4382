# Contributing to LRMIS

## Development Setup

1. Clone the repository
2. Copy `backend/.env.example` to `backend/.env` and fill in your values
3. Follow the setup steps in `README.md`

## Project Structure

```
lrmis/
├── backend/          # FastAPI + MongoDB API
│   ├── app.py        # FastAPI entry point
│   ├── config.py     # Settings via pydantic-settings
│   ├── database.py   # MongoDB/Beanie initialization
│   ├── models.py     # Pydantic & Beanie ODM models
│   ├── requirements.txt
│   ├── .env.example  # Copy to .env and fill in
│   └── routers/
│       ├── applications.py  # Land application workflows
│       ├── applicants.py    # Applicant portal
│       └── staff.py         # Surveyors & registrar
│
└── frontend/         # Streamlit UI
    ├── app.py        # Streamlit entry point
    ├── api.py        # HTTP client helpers
    ├── requirements.txt
    └── pages/        # One file per UI page
```

## Branches
- `main` — stable releases
- `dev` — active development
- Feature branches: `feature/<name>`

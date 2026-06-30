# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ModelGrader-Backend is a competitive programming grading system built with Django 4.1.2 + Django REST Framework. It accepts code submissions in Python, C, and C++, runs them against test cases in sandboxed subprocesses, and scores them.

## Commands

```bash
# Run development server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Run tests
python manage.py test

# Docker build & run (production)
docker build -t grader-backend-prod .
docker run -p 8000:8000 grader-backend-prod
```

Start scripts: `start.sh` (default), `start-dev.sh`, `start-prod.sh`. The Docker entrypoint (`entrypoint.sh`) runs migrations before starting.

## Environment Variables

Copy `.env.example` to `.env` and configure:
- `FRONTEND_URL` — added to CORS allowed origins
- `TOKEN_LIFETIME_HOURS` / `TOKEN_LIFETIME_SECOND` — custom token TTL for session tokens (separate from JWT)

## Architecture

The codebase follows a strict layered pattern: **View → Controller → Repository/Model**.

```
api/
├── views/          # HTTP boundary — parse request, call controller, return response
├── controllers/    # Business logic orchestration (one file per operation)
├── services/       # Domain services (thin layer, some domains)
├── repositories/   # Data access helpers
├── models.py       # All ORM models
├── serializers.py  # DRF serializers
├── sandbox/        # Code execution engine
├── difficulty_predictor/  # ML-based difficulty scoring (pandas/numpy/joblib)
├── errors/         # Custom exception classes
├── permissions/    # DRF permission classes
└── wrappers/       # View decorators
```

Each domain (account, auth, collection, group, problem, submission, topic, script) has its own subdirectory under `views/` and `controllers/`.

### Sandbox / Grading Engine (`api/sandbox/grader.py`)

The grader uses a **10-slot global queue** (`QUEUE = [0]*10`) to cap concurrency. Each slot maps to an isolated directory `section1/` through `section10/`. When a submission arrives:

1. Controller finds a free slot (polls with 5s sleep if all busy) and marks it busy.
2. Grader writes the submitted code to `section{N}/runner.{ext}` and test inputs to `section{N}/testcases/{i}.txt`.
3. For C/C++, it compiles first (`gcc`/`g++`); for Python it runs directly.
4. Each test case runs as a subprocess with a configurable timeout.
5. Output is compared to expected (whitespace-normalized).
6. Slot is released; results are stored as `Submission` + `SubmissionTestcase` records.

Language-specific classes: `PythonGrader`, `CGrader`, `CppGrader` all extend `ProgramGrader`.

### Data Model Key Relationships

- `Account` (UUID PK) → creates `Problem`, `Collection`, `Topic`, `Group`
- `Problem` → has many `Testcase` (input/output pairs)
- `Submission` → belongs to `Account` + `Problem`, has many `SubmissionTestcase`
- `BestSubmission` — one-per (account, problem) tracking highest score
- `Group` → `GroupMember` + fine-grained permissions (`ProblemGroupPermission`, `CollectionGroupPermission`, `TopicGroupPermission`)
- `Topic` → `TopicCollection` → `CollectionProblem` → `Problem` (hierarchical curriculum structure)

Soft deletes: `Testcase` uses a `deprecated` flag; most entities have `is_active`.

### Authentication

Two parallel token systems exist:
1. **JWT** (djangorestframework-simplejwt): `/api/token/` and `/api/token/refresh/` — 5-min access, 1-day refresh.
2. **Custom session token**: stored on `Account` model, used by some endpoints, lifetime controlled by env vars.

Passwords are SHA-512 hashed (no salt — do not extend this pattern).

### API URL Structure

All routes are under `/api/` and follow REST conventions. The 54 routes in `api/urls.py` cover: accounts, problems, testcases, submissions, collections, topics, groups, and admin scripts. JWT token routes are at the root of `api/urls.py`.

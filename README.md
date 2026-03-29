# ResumeOS

ResumeOS is an AI-assisted resume IDE for technical job seekers. The product is centered on safe, reviewable resume edits: the AI proposes structured patches, the user approves changes hunk by hunk, and the document remains under the user's control.

## Project Docs

- [Product Architecture and Production Plan](./docs/product-architecture.md)
- [Implementation Log](./docs/implementation-log.md)
- [Section 2 Blueprint](./docs/section-2-editor-compile.md)

## Current Status

Section 1 is scaffolded:

- `apps/web`: minimal Next.js UI for creating a resume and editing the raw LaTeX working draft
- `apps/api`: FastAPI service for local dev auth, resume CRUD, and draft persistence
- `packages/shared`: shared DTO definitions for resume and user contracts

## Local Development

### API

```bash
cd /Users/mderaznasr/Documents/GitHub/ResumeOS/apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API uses a local SQLite file for the initial Section 1 slice. The schema lives in `apps/api/schema.sql`.

Note: the backend requirements are pinned to versions that work with the currently installed Python 3.14 on this machine.

### Web

```bash
cd /Users/mderaznasr/Documents/GitHub/ResumeOS
npm install
npm run dev:web
```

Set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` if needed. By default the web app expects the API on `http://localhost:8000`.

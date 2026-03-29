CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS resumes (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL,
  slug TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, slug),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS working_drafts (
  id TEXT PRIMARY KEY,
  resume_id TEXT NOT NULL UNIQUE,
  source_tex TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(resume_id) REFERENCES resumes(id)
);

CREATE TABLE IF NOT EXISTS compile_runs (
  id TEXT PRIMARY KEY,
  resume_id TEXT NOT NULL,
  draft_version INTEGER NOT NULL,
  status TEXT NOT NULL,
  log_text TEXT NOT NULL,
  pdf_path TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(resume_id) REFERENCES resumes(id)
);

CREATE TABLE IF NOT EXISTS snapshots (
  id TEXT PRIMARY KEY,
  resume_id TEXT NOT NULL,
  name TEXT NOT NULL,
  source_tex TEXT NOT NULL,
  source_version INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(resume_id) REFERENCES resumes(id)
);

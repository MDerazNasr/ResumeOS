CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  google_sub TEXT UNIQUE,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS users_google_sub_unique
ON users(google_sub)
WHERE google_sub IS NOT NULL;

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

CREATE TABLE IF NOT EXISTS feedback_events (
  id TEXT PRIMARY KEY,
  resume_id TEXT NOT NULL,
  suggestion_mode TEXT NOT NULL,
  action TEXT NOT NULL,
  suggestion_set_id TEXT NOT NULL,
  proposal_id TEXT NOT NULL,
  target_block_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(resume_id) REFERENCES resumes(id)
);

CREATE TABLE IF NOT EXISTS style_examples (
  id TEXT PRIMARY KEY,
  resume_id TEXT NOT NULL,
  source_type TEXT NOT NULL,
  block_kind TEXT NOT NULL,
  block_label TEXT NOT NULL,
  text TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(resume_id, source_type, text),
  FOREIGN KEY(resume_id) REFERENCES resumes(id)
);

CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  token_hash TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS user_settings (
  user_id TEXT PRIMARY KEY,
  editor_mode TEXT NOT NULL DEFAULT 'standard',
  theme_mode TEXT NOT NULL DEFAULT 'light',
  updated_at TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS chat_threads (
  id TEXT PRIMARY KEY,
  resume_id TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(resume_id) REFERENCES resumes(id)
);

CREATE TABLE IF NOT EXISTS chat_messages (
  id TEXT PRIMARY KEY,
  thread_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(thread_id) REFERENCES chat_threads(id)
);

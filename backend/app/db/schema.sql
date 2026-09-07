CREATE TABLE IF NOT EXISTS schema_migrations (
    version    TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS employees (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL UNIQUE,
    name        TEXT    NOT NULL,
    created_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS chats (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL UNIQUE,
    type        TEXT    NOT NULL,
    title       TEXT,
    created_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id      INTEGER NOT NULL REFERENCES chats (id),
    message_id   INTEGER NOT NULL,
    employee_id  INTEGER NOT NULL REFERENCES employees (id),
    text         TEXT    NOT NULL,
    status       TEXT    NOT NULL,
    created_at   TEXT    NOT NULL,
    started_at   TEXT,
    done_at      TEXT,
    cancelled_at TEXT,
    UNIQUE (chat_id, message_id)
);

CREATE INDEX IF NOT EXISTS idx_tasks_employee ON tasks (employee_id, status);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status, created_at);

CREATE TABLE IF NOT EXISTS task_events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id    INTEGER NOT NULL REFERENCES tasks (id) ON DELETE CASCADE,
    status     TEXT    NOT NULL,
    actor_id   INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    text       TEXT    NOT NULL,
    created_at TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_task_events_task ON task_events (task_id, id);

CREATE TABLE IF NOT EXISTS unresolved_messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id    INTEGER NOT NULL REFERENCES chats (id),
    message_id INTEGER NOT NULL,
    text       TEXT    NOT NULL,
    created_at TEXT    NOT NULL,
    UNIQUE (chat_id, message_id)
);
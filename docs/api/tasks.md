# Tasks

Read-only. Statuses change in Telegram, never through the API. All endpoints
require the session cookie.

## GET /api/tasks

The task list. Accepts the [shared filters](filters.md) and the shared
[pagination](filters.md#pagination), plus:

- `search` — case-insensitive substring of the task text.
- `sort` — `created_at`, `-created_at` (default), `done_at`, `-done_at`. Ties
  break on `id` descending.

```json
{
  "items": [{
    "id": 0,
    "text": "",
    "status": "open",
    "message_id": 0,
    "message_link": null,
    "employee": {},
    "chat": {},
    "created_at": "",
    "started_at": null,
    "done_at": null,
    "cancelled_at": null
  }],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

`employee` and `chat` come embedded.

`message_link` — a `t.me/c/...` deep link to the original message. It is `null`
for private chats, which have no linkable form.

## GET /api/tasks/{id}

The same object plus its full history, ascending by time.

```json
{ "events": [{ "id": 0, "status": "open", "actor_name": "", "message_id": 0, "text": "", "created_at": "" }] }
```

`actor_name` — the stored employee name for that Telegram id, or the raw id when
the actor is not an employee, which is the case for the manager's own events.

`404` — `{ "detail": "Not found" }` when the task does not exist.

## GET /api/unresolved

Messages tagged `#task` whose assignee could not be resolved. Same envelope and
pagination as `/api/tasks`; honors `period`, `chat_id` and `chat_type` only.
Sorted by `created_at` descending, ties broken on `id`.

```json
{ "items": [{ "id": 0, "chat": {}, "message_id": 0, "message_link": null, "text": "", "created_at": "" }] }
```

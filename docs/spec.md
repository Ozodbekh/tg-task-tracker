# Spec

Agreed decisions. Code follows this file. Open questions stay open until
answered here.

## Purpose

The manager assigns tasks to employees in Telegram. The system captures those
tasks and tracks them.

## Telegram access

- Telethon user session on the manager's account. No Bot API bot.
- Sources: one-to-one chats and groups.

## Task capture

- A message creates a task when it contains `#task`.
- Only messages sent by the manager (outgoing) create tasks.
- Assignee resolution:
  - One-to-one chat: the other party of the chat.
  - Group: the mentioned user. A user without a username cannot be mentioned by
    `@username`, so all three forms are supported, in this order:
    1. a text mention, which carries the `user_id` directly
    2. an `@username` mention
    3. a reply to the assignee's message, when no mention is present
  - A name typed as plain text is not a mention and carries no `user_id`. Only
    real mention entities count.
  - Group, none of the three present: no task is created; the message is
    recorded as unresolved.
- The assignee's `user_id` and name are taken from the resolved Telegram user.
- Media captions count as message text.

## Origin

Every task stores where it came from:

- `chat_id` and `message_id`
- chat type: private or group
- chat title, for groups

This is what lets the web panel link back to the original message.

## Status

- A task starts as `open`.
- The assignee replies to the task message to change its status:
  - `#inp` moves it to `in_progress`
  - `#onhold` moves it to `on_hold`, paused by the assignee
  - `#blocked` moves it to `blocked`, waiting on someone else
  - `#done` moves it to `done`
  - `#cancel` moves it to `cancelled`
- A message carrying more than one status tag takes the first one in the text.
- Only `in_progress`, `done` and `cancelled` stamp a column on the task row.
  `on_hold` and `blocked` are recorded as events only.
- Works in one-to-one chats and groups.
- A status reply is accepted only from the task's assignee. Replies from anyone
  else are ignored.
- The task a reply refers to is resolved by `chat_id` plus the replied-to
  `message_id`. A `message_id` is unique only within its chat, so the pair is
  the lookup key.
- Status replies are tracked on edit too. A mistyped tag corrected by an edit,
  such as `#don` becoming `#done`, is picked up and applied.

## History

Every status change is stored as an event, not only as a column:

- which task
- which status
- who sent it, and the `message_id` of their message
- the text sent along with the tag
- the time it happened

The task row keeps the current status and its timestamps for fast listing; the
events keep the full history, the comments written next to a tag, and the time
spent in each status.

## Edits

- Edited messages are handled through `MessageEdited`, in one-to-one chats and
  groups alike.
- A task is identified by `chat_id` + `message_id`, unique.
- `#task` added by an edit creates the task.
- Text edited while `#task` remains updates the task text.
- A mention added or changed by an edit updates the assignee.
- `#task` removed by an edit moves the task to `cancelled`. Nothing is deleted.
- Edits made while the client is offline are not redelivered by Telegram and
  may be missed.

## Backfill

A chat's history can be replayed on demand with `python -m app.backfill
<chat_id> [--apply]`. It reads the chat oldest to newest through the same
parser and tags as the live listener, and stores each message with its own
date rather than the time of the run.

It never touches a task that is already stored, and applies a status reply only
to a task captured in the same run, so a replay cannot undo what the listener
has already recorded.

## Leaving

An employee who leaves is marked, never deleted; their task history has to
survive. `employees.left_at` carries the moment.

Retiring cancels every task of theirs that is not finished, so unfinished work
does not sit forever against someone who is gone. The daily digest skips them
and the bot tells them they are no longer active. They stay in the employee
list so their past work can still be filtered.

## Open

- Deadlines.
- Web panel scope and access.
- Several mentions in one message: whether the ones after the first should get
  a task of their own. That needs `tasks` to be unique on
  `(chat_id, message_id, employee_id)`, which is a migration.

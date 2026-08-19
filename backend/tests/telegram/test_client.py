import sqlite3
from contextlib import closing
from pathlib import Path

from app.telegram.client import clone_session


async def test_clone_session_copies_a_database_another_process_holds(
    tmp_path: Path,
) -> None:
    source = tmp_path / "manager.session"
    target = tmp_path / "digest.session"

    with closing(sqlite3.connect(source)) as holder:
        holder.execute("CREATE TABLE sessions (auth_key BLOB)")
        holder.execute("INSERT INTO sessions VALUES (?)", (b"key",))
        holder.commit()

        await clone_session(source, target)

    with closing(sqlite3.connect(target)) as copy:
        stored = copy.execute("SELECT auth_key FROM sessions").fetchone()
    assert stored == (b"key",)

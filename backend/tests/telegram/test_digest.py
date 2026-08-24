import asyncio

import pytest

from app.models.digest import EmployeeDigest
from app.models.stats import StatusCounts
from app.telegram.digest import MAX_PAUSE_SECONDS, MIN_PAUSE_SECONDS, DigestSender


class FakeClient:
    def __init__(self, failing: set[int] | None = None) -> None:
        self.sent: list[int] = []
        self._failing = failing or set()

    async def send_message(self, entity: int, message: str, parse_mode: str) -> None:
        if entity in self._failing:
            raise RuntimeError("blocked")
        self.sent.append(entity)


@pytest.fixture
def pauses(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    recorded: list[float] = []

    async def record(seconds: float) -> None:
        recorded.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", record)
    return recorded


def digest_of(telegram_id: int) -> EmployeeDigest:
    return EmployeeDigest(
        telegram_id=telegram_id,
        name=f"Employee {telegram_id}",
        total=1,
        by_status=StatusCounts(open=1),
    )


async def test_send_pauses_between_messages_but_not_before_the_first(
    pauses: list[float],
) -> None:
    client = FakeClient()

    delivered = await DigestSender(client).send([digest_of(i) for i in (1, 2, 3)])

    assert delivered == 3
    assert client.sent == [1, 2, 3]
    assert len(pauses) == 2
    assert all(MIN_PAUSE_SECONDS <= pause <= MAX_PAUSE_SECONDS for pause in pauses)


async def test_send_keeps_pacing_after_a_failed_message(pauses: list[float]) -> None:
    client = FakeClient(failing={2})

    delivered = await DigestSender(client).send([digest_of(i) for i in (1, 2, 3)])

    assert delivered == 2
    assert client.sent == [1, 3]
    assert len(pauses) == 2


async def test_a_single_employee_is_not_delayed(pauses: list[float]) -> None:
    await DigestSender(FakeClient()).send([digest_of(1)])

    assert pauses == []

import httpx
import pytest

from app.bot.webhook import SECRET_HEADER, WEBHOOK_PATH

UPDATE = {"update_id": 1}


async def test_webhook_rejects_a_missing_secret(client: httpx.AsyncClient) -> None:
    response = await client.post(WEBHOOK_PATH, json=UPDATE)

    assert response.status_code == 403


async def test_webhook_rejects_a_wrong_secret(client: httpx.AsyncClient) -> None:
    response = await client.post(
        WEBHOOK_PATH, json=UPDATE, headers={SECRET_HEADER: "guess"}
    )

    assert response.status_code == 403


async def test_webhook_needs_no_session_cookie(client: httpx.AsyncClient) -> None:
    response = await client.post(WEBHOOK_PATH, json=UPDATE)

    assert response.status_code != 401


@pytest.mark.parametrize("path", ["/api/tasks?period=month", "/api/employees"])
async def test_the_rest_of_the_api_is_still_protected(
    client: httpx.AsyncClient, path: str
) -> None:
    assert (await client.get(path)).status_code == 401

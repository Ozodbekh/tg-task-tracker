import httpx
import pytest

PROTECTED = [
    "/api/stats/overview?period=month",
    "/api/stats/timeseries?period=month",
    "/api/stats/employees?period=month",
    "/api/stats/chats?period=month",
    "/api/tasks?period=month",
    "/api/employees",
    "/api/chats",
    "/api/unresolved?period=month",
]


@pytest.mark.parametrize("path", PROTECTED)
async def test_endpoints_require_a_session(
    client: httpx.AsyncClient, path: str
) -> None:
    assert (await client.get(path)).status_code == 401


async def test_overview(signed_in: httpx.AsyncClient) -> None:
    response = await signed_in.get("/api/stats/overview?period=year")
    assert response.status_code == 200

    body = response.json()
    counts = body["by_status"]
    assert body["total"] == sum(counts.values())
    assert 0.0 <= body["completion_rate"] <= 1.0
    assert body["previous"] is not None
    assert set(counts) == {"open", "in_progress", "done", "cancelled"}


async def test_overview_for_all_has_no_previous_window(
    signed_in: httpx.AsyncClient,
) -> None:
    body = (await signed_in.get("/api/stats/overview?period=all")).json()
    assert body["previous"] is None


async def test_status_filter_narrows_every_endpoint(
    signed_in: httpx.AsyncClient,
) -> None:
    overview = (
        await signed_in.get("/api/stats/overview?period=year&status=done")
    ).json()
    assert overview["by_status"]["open"] == 0
    assert overview["total"] == overview["by_status"]["done"]

    tasks = (await signed_in.get("/api/tasks?period=year&status=done")).json()
    assert {item["status"] for item in tasks["items"]} == {"done"}


async def test_timeseries_has_no_gaps(signed_in: httpx.AsyncClient) -> None:
    points = (
        await signed_in.get("/api/stats/timeseries?period=week&bucket=day")
    ).json()
    assert len(points) >= 7
    assert points == sorted(points, key=lambda point: point["bucket"])
    assert all("+05:00" in point["bucket"] for point in points)


async def test_tasks_pagination_and_embedded_rows(
    signed_in: httpx.AsyncClient,
) -> None:
    body = (await signed_in.get("/api/tasks?period=all&page_size=5")).json()
    assert body["page"] == 1
    assert body["page_size"] == 5
    assert len(body["items"]) == 5
    assert body["total"] > 5

    item = body["items"][0]
    assert item["employee"]["name"]
    assert item["chat"]["type"] in {"private", "group"}
    if item["chat"]["type"] == "group":
        assert item["message_link"].startswith("https://t.me/c/")
    else:
        assert item["message_link"] is None


async def test_tasks_search(signed_in: httpx.AsyncClient) -> None:
    body = (await signed_in.get("/api/tasks?period=all&search=report")).json()
    assert body["total"] > 0
    assert all("report" in item["text"] for item in body["items"])


async def test_task_detail_carries_history(signed_in: httpx.AsyncClient) -> None:
    listed = (await signed_in.get("/api/tasks?period=all&status=done")).json()
    task_id = listed["items"][0]["id"]

    body = (await signed_in.get(f"/api/tasks/{task_id}")).json()
    assert body["id"] == task_id
    assert body["events"][0]["status"] == "open"
    assert all(event["actor_name"] for event in body["events"])


async def test_unknown_task_is_not_found(signed_in: httpx.AsyncClient) -> None:
    assert (await signed_in.get("/api/tasks/999999")).status_code == 404


async def test_employee_stats(signed_in: httpx.AsyncClient) -> None:
    employees = (await signed_in.get("/api/employees")).json()
    assert employees == sorted(employees, key=lambda row: row["name"])

    employee_id = employees[0]["id"]
    body = (
        await signed_in.get(f"/api/employees/{employee_id}/stats?period=year")
    ).json()
    assert body["employee"]["id"] == employee_id
    assert body["total"] >= 0


async def test_unknown_employee_is_not_found(signed_in: httpx.AsyncClient) -> None:
    response = await signed_in.get("/api/employees/999999/stats?period=year")
    assert response.status_code == 404


async def test_chat_stats(signed_in: httpx.AsyncClient) -> None:
    body = (await signed_in.get("/api/stats/chats?period=year")).json()
    rows = body["items"]
    assert body["total"] >= len(rows)
    assert rows == sorted(rows, key=lambda row: row["total"], reverse=True)
    assert all(row["participants"] >= 0 for row in rows)


@pytest.mark.parametrize(
    "path", ["/api/stats/employees", "/api/stats/chats", "/api/unresolved"]
)
async def test_list_endpoints_share_the_envelope(
    signed_in: httpx.AsyncClient, path: str
) -> None:
    body = (await signed_in.get(f"{path}?period=year&page_size=2")).json()
    assert set(body) == {"items", "total", "page", "page_size"}
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert len(body["items"]) <= 2


async def test_top_n_page_is_a_prefix_of_the_full_ranking(
    signed_in: httpx.AsyncClient,
) -> None:
    top = (await signed_in.get("/api/stats/employees?period=all&page_size=3")).json()
    full = (await signed_in.get("/api/stats/employees?period=all&page_size=100")).json()

    assert top["total"] == full["total"]
    assert [row["employee"]["id"] for row in top["items"]] == [
        row["employee"]["id"] for row in full["items"][:3]
    ]


async def test_pages_do_not_repeat_rows(signed_in: httpx.AsyncClient) -> None:
    first = (await signed_in.get("/api/tasks?period=all&page=1&page_size=25")).json()
    second = (await signed_in.get("/api/tasks?period=all&page=2&page_size=25")).json()

    ids = {item["id"] for item in first["items"]}
    assert ids.isdisjoint({item["id"] for item in second["items"]})
    assert first["total"] == second["total"]


async def test_page_past_the_end_is_empty_not_missing(
    signed_in: httpx.AsyncClient,
) -> None:
    response = await signed_in.get("/api/tasks?period=all&page=9999")
    assert response.status_code == 200

    body = response.json()
    assert body["items"] == []
    assert body["total"] > 0


async def test_page_size_is_clamped_not_rejected(
    signed_in: httpx.AsyncClient,
) -> None:
    body = (await signed_in.get("/api/tasks?period=all&page_size=500")).json()
    assert body["page_size"] == 100
    assert len(body["items"]) <= 100


async def test_unresolved_list(signed_in: httpx.AsyncClient) -> None:
    body = (await signed_in.get("/api/unresolved?period=year")).json()
    assert body["total"] > 0
    assert all(item["chat"]["type"] == "group" for item in body["items"])


@pytest.mark.parametrize(
    "query",
    [
        "period=decade",
        "period=month&bucket=fortnight",
        "period=month&status=paused",
        "period=month&chat_type=channel",
        "period=month&sort=text",
        "period=month&page=0",
    ],
)
async def test_invalid_filters_are_rejected(
    signed_in: httpx.AsyncClient, query: str
) -> None:
    response = await signed_in.get(f"/api/tasks?{query}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid filters"}

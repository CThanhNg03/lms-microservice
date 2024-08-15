import asyncio
from httpx import AsyncClient
import pytest

from app.model import conversation

from .main import app

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": "Bearer 123asaf234"
}

@pytest.mark.anyio
async def test_create_conversation():
    async with AsyncClient(app, base_url="http://localhost:8000") as client:
        response = await client.post(
            "/create_conversation",
            json={
                "members": [123, 345, 357]
            },
            headers=headers
        )

        assert response.status_code == 201, response.text
        assert response.json().get("members") == [123, 345, 357]

        conversation_id = response.json().get("id")
        
        response = await client.get(
            f"/get_conversation/{conversation_id}",
            headers=headers
        )

        assert response.status_code == 200, response.text
        assert response.json().get("id") == conversation_id
        assert response.json().get("members") == [123, 345, 357]

@pytest.mark.anyio
async def test_create_conversation_without_user():
    async with AsyncClient(app, base_url="http://localhost:8000") as client:
        response = await client.post(
            "/create_conversation",
            json={
                "members": [345]
            },
            headers=headers
        )

    assert response.status_code == 201, response.text
    assert response.json().get("members") == [123, 345]

    conversation_id = response.json().get("id")

    async with AsyncClient(app, base_url="http://localhost:8000") as client:
        response = await client.get(
            f"/get_conversation/{conversation_id}",
            headers=headers
        )

    assert response.status_code == 200, response.text
    assert response.json().get("id") == conversation_id
    assert response.json().get("members") == [123, 345]

@pytest.mark.anyio
async def test_get_my_conversations():
    async with AsyncClient(app, base_url="http://localhost:8000") as client:
        response = await client.get(
            "/get_my_conversations",
            headers=headers
        )

    assert response.status_code == 200, response.text
    assert len(response.json()) > 0

@pytest.mark.anyio
async def test_get_my_recent_chat():
    async with AsyncClient(app, base_url="http://localhost:8000") as client:
        response = await client.get(
            "/get_my_recent_chat",
            headers=headers
        )

    assert response.status_code == 200, response.text
    assert len(response.json()) > 0

@pytest.mark.anyio
async def test_chat():
    token1 = "123asaf234"
    token2 = "345asaf234sf"

    async with AsyncClient(app, base_url="http://localhost:8000") as client:
        response = await client.post(
            "/new_direct_message",
            json= {
                "members": [345],
                "title": ""
            },
            headers= headers
        )
    assert response.status_code == 200, response.text
    conversation_id = response.json().get("id")

    async def connect_ws(token, user_id):
        async with AsyncClient(app, base_url="http://localhost:8000") as client:
            async with client.websocket_connect(f"ws/{conversation_id}?token={token}") as ws:
                await ws.send_json({"type": "connect"})
                response = await ws.receive_json()
                assert response.get("type") == "connect"
                
                await ws.send_json({"type": "message", "content": f"Hello from {user_id}"})
                response = await ws.receive_json()

                assert response.get("type") == "message"
    
    task_user1 = asyncio.ensure_future(connect_ws(token1, 123))
    task_user2 = asyncio.ensure_future(connect_ws(token2, 345))

    await asyncio.gather(task_user1, task_user2)



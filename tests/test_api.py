import pytest
from httpx import AsyncClient
from app.main import app
from app.database import db
import uuid
import time
import asyncio

@pytest.mark.asyncio
async def test_order_flow(queue_fixture):
    order_id = f"test_order_{uuid.uuid4().hex}"
    order_data = {
        "user_id": "test_user",
        "order_id": order_id,
        "item_ids": ["item1", "item2"],
        "total_amount": 99.99
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test order creation
        response = await client.post("/orders", json=order_data)
        assert response.status_code == 201

        # Verify processing within 5 seconds
        start_time = time.time()
        while time.time() - start_time < 5:
            response = await client.get(f"/orders/{order_id}/status")
            if response.json()["status"] == "Completed":
                break
            await asyncio.sleep(0.5)
        else:
            pytest.fail("Order processing timed out")

    # Cleanup
    async with db.session() as conn:
        await conn.execute("DELETE FROM orders WHERE order_id = $1", order_id)
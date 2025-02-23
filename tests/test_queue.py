import pytest
import asyncio
import uuid
from app.database import db
from app.queue_processor import queue
import time

@pytest.mark.asyncio
async def test_order_processing(queue_fixture):
    order_id = f"test_queue_{uuid.uuid4().hex}"
    try:
        async with db.session() as conn:
            await conn.execute(
                "INSERT INTO orders (order_id, user_id, item_ids, total_amount) "
                "VALUES ($1, $2, $3::jsonb, $4)",
                order_id,
                "user_1",
                '["item1"]',
                50.0
            )

        await queue_fixture.enqueue(order_id)

        # Verify processing
        start_time = time.time()
        while time.time() - start_time < 5:
            async with db.session() as conn:
                record = await conn.fetchrow(
                    "SELECT status FROM orders WHERE order_id = $1", order_id
                )
                if record["status"] == "Completed":
                    break
                await asyncio.sleep(0.1)
        else:
            pytest.fail("Order processing timed out")
    finally:
        async with db.session() as conn:
            await conn.execute("DELETE FROM orders WHERE order_id = $1", order_id)
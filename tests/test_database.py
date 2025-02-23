import pytest
from app.database import db
import uuid

@pytest.mark.asyncio
async def test_database_connection():
    assert db.pool is not None
    async with db.session() as conn:
        await conn.execute("SELECT 1")

@pytest.mark.asyncio
async def test_order_creation():
    order_id = f"test_order_{uuid.uuid4().hex}"
    try:
        async with db.session() as conn:
            await conn.execute(
                "INSERT INTO orders (order_id, user_id, item_ids, total_amount) "
                "VALUES ($1, $2, $3::jsonb, $4)",
                order_id,
                "user_1",
                '["item1", "item2"]',
                100.0
            )
            record = await conn.fetchrow(
                "SELECT * FROM orders WHERE order_id = $1", order_id
            )
            assert record["status"] == "Pending"
    finally:
        async with db.session() as conn:
            await conn.execute("DELETE FROM orders WHERE order_id = $1", order_id)
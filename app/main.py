import asyncpg
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from .database import db
from .queue_processor import queue
from .metrics import calculate_metrics
import asyncio
import json

app = FastAPI()

class OrderCreate(BaseModel):
    user_id: str
    order_id: str
    item_ids: list[str]
    total_amount: float

@app.on_event("startup")
async def startup():
    await db.connect()
    asyncio.create_task(queue.process_orders())
    await restore_pending_orders()

async def restore_pending_orders():
    async with db.session() as conn:
        records = await conn.fetch(
            "SELECT order_id FROM orders WHERE status = 'Pending'"
        )
        for record in records:
            await queue.enqueue(record["order_id"])

@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate):
    async with db.session() as conn:
        try:
            await conn.execute(
                "INSERT INTO orders (order_id, user_id, item_ids, total_amount) "
                "VALUES ($1, $2, $3, $4)",
                order.order_id, order.user_id, json.dumps(order.item_ids), order.total_amount
            )
            await queue.enqueue(order.order_id)
            return {"message": "Order created successfully"}
        except asyncpg.UniqueViolationError:
            raise HTTPException(
                status_code=400,
                detail="Order ID already exists"
            )

@app.get("/orders/{order_id}/status")
async def get_status(order_id: str):
    async with db.session() as conn:
        record = await conn.fetchrow(
            "SELECT status FROM orders WHERE order_id = $1",
            order_id
        )
        if not record:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"status": record["status"]}

@app.get("/metrics")
async def get_metrics():
    return await calculate_metrics()
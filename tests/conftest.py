import pytest
import asyncio
from app.database import db
from app.queue_processor import queue, OrderQueue

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def db_fixture():
    await db.connect()
    yield
    await db.close()

@pytest.fixture(autouse=True)
async def queue_fixture(event_loop):
    # Create new queue instance with test event loop
    test_queue = OrderQueue(loop=event_loop)
    processor_task = event_loop.create_task(test_queue.process_orders())
    yield test_queue
    await test_queue.stop()
    processor_task.cancel()
    try:
        await processor_task
    except asyncio.CancelledError:
        pass
import asyncio
from app.database import db

class OrderQueue:
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.queue = asyncio.Queue(loop=self.loop)
        self.processing = set()
        self._running = True

    async def enqueue(self, order_id):
        await self.queue.put(order_id)

    async def process_orders(self):
        while self._running:
            try:
                order_id = await asyncio.wait_for(self.queue.get(), timeout=1)
                self.processing.add(order_id)
                async with db.session() as conn:
                    await conn.execute(
                        "UPDATE orders SET status = 'Processing', "
                        "processing_started_at = NOW() WHERE order_id = $1",
                        order_id
                    )
                    await asyncio.sleep(2)
                    await conn.execute(
                        "UPDATE orders SET status = 'Completed', "
                        "completed_at = NOW() WHERE order_id = $1",
                        order_id
                    )
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing order {order_id}: {str(e)}")
            finally:
                if order_id in self.processing:
                    self.processing.remove(order_id)
                self.queue.task_done()

    async def stop(self):
        self._running = False
        await self.queue.join()

queue = OrderQueue()
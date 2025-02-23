import os
import asyncpg
from contextlib import asynccontextmanager
import asyncio

class Database:
    def __init__(self):
        self.pool = None
        self._lock = asyncio.Lock()

    async def connect(self):
        async with self._lock:
            if not self.pool:
                self.pool = await asyncpg.create_pool(
                    os.getenv("DB_URL", "postgresql://shubham@localhost/ecommerce"),
                    min_size=5,
                    max_size=20
                )
                await self._initialize_db()

    async def _initialize_db(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                DO $$ BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'order_status') THEN
                        CREATE TYPE order_status AS ENUM ('Pending', 'Processing', 'Completed');
                    END IF;
                END $$;
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    item_ids JSONB NOT NULL,
                    total_amount DECIMAL NOT NULL,
                    status order_status DEFAULT 'Pending',
                    created_at TIMESTAMP DEFAULT NOW(),
                    processing_started_at TIMESTAMP,
                    completed_at TIMESTAMP
                );
            """)

    async def close(self):
        async with self._lock:
            if self.pool:
                await self.pool.close()
                self.pool = None

    @asynccontextmanager
    async def session(self):
        await self.connect()
        conn = await self.pool.acquire()
        try:
            yield conn
        finally:
            await self.pool.release(conn)

db = Database()
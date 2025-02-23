from .database import db

async def calculate_metrics():
    async with db.session() as conn:
        return {
            "total_orders": await _get_total_orders(conn),
            "average_processing_time": await _get_avg_processing_time(conn),
            "status_counts": await _get_status_counts(conn)
        }

async def _get_total_orders(conn):
    return await conn.fetchval("SELECT COUNT(*) FROM orders")

async def _get_avg_processing_time(conn):
    return await conn.fetchval("""
        SELECT AVG(EXTRACT(EPOCH FROM (completed_at - processing_started_at)))
        FROM orders WHERE status = 'Completed'
    """) or 0

async def _get_status_counts(conn):
    counts = {}
    records = await conn.fetch(
        "SELECT status, COUNT(*) as count FROM orders GROUP BY status"
    )
    for record in records:
        counts[record["status"]] = record["count"]
    return counts
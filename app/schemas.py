from pydantic import BaseModel
from typing import List

class OrderCreate(BaseModel):
    user_id: str
    order_id: str
    item_ids: List[str]
    total_amount: float

class OrderStatusResponse(BaseModel):
    status: str

class MetricsResponse(BaseModel):
    total_orders: int
    average_processing_time: float
    status_counts: dict
# E-commerce Order Processing System

A scalable backend system for handling e-commerce orders with async processing.

## Features
- RESTful API for order management
- Async order processing with in-memory queue
- Real-time metrics reporting
- PostgreSQL database integration
- Unit tests for core components

## Setup

1. **Prerequisites**
    - Python 3.8+
    - PostgreSQL 12+

2. **Install dependencies**
  ```bash
  pip3 install -r requirements.txt
  ```

3. **Database Setup**
  ```bash
  createdb ecommerce
  psql -d ecommerce -f sql/schema.sql
  ```

4. **Run the Application**
  ```bash
  python3 -m uvicorn app.main:app --reload
  ```

5. ** Run the test suits **
  ```bash
  python3 -m pytest -v tests/
  ```

## API Documentation

### Create Order
  ```bash
  curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "order_id": "order1", "item_ids": ["item1"], "total_amount": 50.0}'
  ```
  ```json
  {
    "message":"Order created successfully"
  }
  ```

### Get Order Status
  ```bash
  curl "http://localhost:8000/orders/order1/status"
  ```
  ```json
  {
    "status": "Pending"
  }
  ```

### Get Metrics
  ```bash
  curl "http://localhost:8000/metrics"
  ```
  ```json
  {
    "total_orders": 12,
    "average_processing_time": 2.003636,
    "status_counts": {
      "Processing": 5,
      "Pending": 2,
      "Completed": 5
    }
  }
  ```
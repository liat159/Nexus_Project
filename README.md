# Nexus Digital Coupon Marketplace - Backend

This is a backend system for a digital marketplace that sells coupon-based products through direct customers and external resellers via a REST API.

## Tech Stack
- **Language**: Python 3.10
- **Framework**: FastAPI (for high performance and easy REST API routing)
- **Database**: SQLite (via SQLAlchemy ORM)
- **Containerization**: Docker

## Business Logic Enforced
- **Server-Side Pricing**: `minimum_sell_price` is strictly calculated server-side based on the formula `cost_price × (1 + margin_percentage / 100)`.
- **Atomic Purchases**: Products are marked as sold immediately upon successful transaction.
- **Reseller Rules**: Resellers are blocked from purchasing if their `reseller_price` is below the `minimum_sell_price`.
- **Security**: The Reseller API is protected by Bearer Token Authentication.

## Running the Application Locally (with Docker)

1. **Build the Docker image:**
   ```bash
   docker build -t nexus-backend .
Run the Docker container:

Bash
docker run -d -p 8000:8000 --name nexus-app nexus-backend
Access the API:

The API will be available at http://localhost:8000

Interactive Swagger API Documentation is available at: http://localhost:8000/docs

Usage Examples
1. Admin - Create a Product
Bash
curl -X 'POST' \
  'http://localhost:8000/admin/products' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Amazon $100 Coupon",
  "description": "Gift card",
  "image_url": "[https://example.com/image.png](https://example.com/image.png)",
  "cost_price": 80,
  "margin_percentage": 25,
  "value_type": "STRING",
  "value": "ABCD-1234"
}'
2. Reseller - Get Available Products
Requires Bearer Token authentication (my-secret-token).

Bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/products' \
  -H 'Authorization: my-secret-token'
3. Reseller - Purchase a Product
Bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/products/{product_id}/purchase' \
  -H 'Authorization: my-secret-token' \
  -H 'Content-Type: application/json' \
  -d '{
  "reseller_price": 120.00
}'
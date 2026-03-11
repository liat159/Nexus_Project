# Nexus Digital Coupon Marketplace

This is a complete solution for a digital marketplace that sells coupon-based products. The project includes a robust REST API backend designed with a clean architecture, alongside a minimal, functional frontend to demonstrate both Admin and Customer workflows.

## 🛠️ Tech Stack & Architecture
- **Backend**: Python 3.10, FastAPI, SQLite (via SQLAlchemy ORM)
- **Frontend**: Vanilla HTML, CSS, and JavaScript (No build tools required)
- **Containerization**: Docker

**Project Structure**:
The application follows a clean layered architecture (Controllers/Services/Models) to ensure maintainability and separation of concerns:
- `main.py`: API Routers, Controllers, Security, and custom Exception Handlers.
- `services.py`: Core business logic and transaction management.
- `models.py`: Database entities and Enums (`ProductType`, `ValueType`).
- `schemas.py`: Pydantic models for request/response validation.
- `database.py`: Database connection and session management.

## ✨ Key Features Enforced
- **Strict Error Formatting**: Custom exception handlers ensure errors are strictly returned as `{"error_code": "...", "message": "..."}` according to requirements.
- **Admin CRUD Operations**: Full control over inventory adhering to REST principles.
- **Server-Side Pricing**: `minimum_sell_price` is strictly calculated server-side based on the formula `cost_price × (1 + margin_percentage / 100)`.
- **Atomic Purchases**: Products are marked as sold immediately upon a successful transaction to prevent double-spending.
- **Separated Channels**: Dedicated endpoints for direct Customers (buying at minimum price) and Resellers (bidding their own price, authenticated via Bearer Token).

## 🚀 How to Run the Application

### 1. Start the Backend Server

**Option A: Locally using Python**
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows: .\venv\Scripts\activate
Install dependencies:

Bash
pip install -r requirements.txt
Run the server:

Bash
python -m uvicorn main:app --reload
Option B: Using Docker

Bash
docker build -t nexus-backend .
docker run -d -p 8000:8000 --name nexus-app nexus-backend
2. Open the Frontend UI
Once the backend is running (locally or via Docker on port 8000), simply open the index.html file in any modern web browser. The UI includes Admin creation/inventory and a Customer storefront.

3. API Documentation
Interactive Swagger API documentation is available at: http://localhost:8000/docs

📡 API Usage Examples (cURL)
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
2. Direct Customer - Purchase a Product
(No Token Required)

Bash
curl -X 'POST' \
  'http://localhost:8000/customer/products/{product_id}/buy' \
  -H 'Content-Type: application/json'
3. Reseller - Purchase a Product
(Requires Bearer Token)

Bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/products/{product_id}/purchase' \
  -H 'Authorization: Bearer my-secret-token' \
  -H 'Content-Type: application/json' \
  -d '{
  "reseller_price": 120.00
}'
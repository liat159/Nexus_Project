from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from database import engine, Base, get_db
from models import ProductDB
from schemas import ProductCreate, ProductUpdate, ProductResponse, PurchaseRequest, PurchaseResponse
from services import ProductException, create_product, get_available_products, purchase_reseller, purchase_direct

# Initialize DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus Digital Coupon Marketplace")

# --- CORS SETUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- CUSTOM EXCEPTION HANDLER ---
# מוודא שהשגיאות חוזרות בדיוק בפורמט שביקשו באפיון


@app.exception_handler(ProductException)
async def custom_product_exception_handler(request: Request, exc: ProductException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.message}
    )

# --- SECURITY ---
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "my-secret-token":
        raise ProductException(401, "UNAUTHORIZED", "Invalid token")
    return credentials.credentials

# ==========================================
#               RESELLER API
# ==========================================


@app.get("/api/v1/products", response_model=List[ProductResponse])
def api_get_products(db: Session = Depends(get_db), token: str = Depends(verify_token)):
    products = get_available_products(db)
    return [{"id": p.id, "name": p.name, "description": p.description, "image_url": p.image_url, "price": p.minimum_sell_price} for p in products]


@app.post("/api/v1/products/{product_id}/purchase", response_model=PurchaseResponse)
def api_purchase_reseller(product_id: str, req: PurchaseRequest, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    product = purchase_reseller(db, product_id, req.reseller_price)
    return PurchaseResponse(
        product_id=product.id,
        final_price=req.reseller_price,
        value_type=product.value_type.value,
        value=product.value
    )

# ==========================================
#           DIRECT CUSTOMER API
# ==========================================


@app.post("/customer/products/{product_id}/buy", response_model=PurchaseResponse)
def api_purchase_direct(product_id: str, db: Session = Depends(get_db)):
    product = purchase_direct(db, product_id)
    return PurchaseResponse(
        product_id=product.id,
        final_price=product.minimum_sell_price,
        value_type=product.value_type.value,
        value=product.value
    )

# ==========================================
#                 ADMIN API
# ==========================================

# Create - יצירת מוצר חדש

# Create - יצירת מוצר חדש (מוגן)


@app.post("/admin/products", status_code=201)
def api_create_product(req: ProductCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    new_product = create_product(db, req)
    return {"message": "Product created successfully", "id": new_product.id}

# Read - קבלת כל המוצרים למנהל (מוגן)


@app.get("/admin/products")
def admin_get_all_products(db: Session = Depends(get_db), token: str = Depends(verify_token)):
    products = db.query(ProductDB).all()
    return products

# Update - עדכון מוצר קיים (מוגן)


@app.put("/admin/products/{product_id}")
def update_product(product_id: str, req: ProductUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise ProductException(404, "PRODUCT_NOT_FOUND", "Product not found")

    update_data = req.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(product, key, val)

    if "cost_price" in update_data or "margin_percentage" in update_data:
        if product.cost_price < 0 or product.margin_percentage < 0:
            raise ProductException(
                400, "INVALID_PRICING", "Pricing fields must be positive")
        product.minimum_sell_price = product.cost_price * \
            (1 + product.margin_percentage / 100)

    db.commit()
    db.refresh(product)
    return {"message": "Product updated successfully", "product": product}

# Delete - מחיקת מוצר (מוגן)


@app.delete("/admin/products/{product_id}", status_code=204)
def delete_product(product_id: str, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise ProductException(404, "PRODUCT_NOT_FOUND", "Product not found")

    db.delete(product)
    db.commit()
    return

from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import List, Optional

# Database setup (SQLite for simplicity)
SQLALCHEMY_DATABASE_URL = "sqlite:///./nexus_marketplace.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- DOMAIN MODEL ---


class ProductDB(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True,
                default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(String, default="COUPON")
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    cost_price = Column(Float, nullable=False)
    margin_percentage = Column(Float, nullable=False)
    minimum_sell_price = Column(Float, nullable=False)
    is_sold = Column(Boolean, default=False)

    value_type = Column(String, nullable=False)  # STRING or IMAGE
    value = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)

# --- SCHEMAS ---


class ProductCreate(BaseModel):
    name: str
    description: str
    image_url: str
    cost_price: float
    margin_percentage: float
    value_type: str
    value: str


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    image_url: str
    price: float


class PurchaseRequest(BaseModel):
    reseller_price: float


class PurchaseResponse(BaseModel):
    product_id: str
    final_price: float
    value_type: str
    value: str


# --- APP INIT ---
app = FastAPI(title="Nexus Digital Coupon Marketplace")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- MIDDLEWARE & AUTH ---


# --- MIDDLEWARE & AUTH ---
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != "my-secret-token":
        raise HTTPException(status_code=401, detail={
                            "error_code": "UNAUTHORIZED", "message": "Invalid token"})
    return token

# --- RESELLER API ---


@app.get("/api/v1/products", response_model=List[ProductResponse])
def get_available_products(db: Session = Depends(get_db), token: str = Depends(verify_token)):
    products = db.query(ProductDB).filter(ProductDB.is_sold == False).all()
    return [{"id": p.id, "name": p.name, "description": p.description, "image_url": p.image_url, "price": p.minimum_sell_price} for p in products]


@app.get("/api/v1/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    product = db.query(ProductDB).filter(
        ProductDB.id == product_id, ProductDB.is_sold == False).first()
    if not product:
        raise HTTPException(status_code=404, detail={
                            "error_code": "PRODUCT_NOT_FOUND", "message": "Product not found"})
    return {"id": product.id, "name": product.name, "description": product.description, "image_url": product.image_url, "price": product.minimum_sell_price}


@app.post("/api/v1/products/{product_id}/purchase", response_model=PurchaseResponse)
def purchase_product(product_id: str, req: PurchaseRequest, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail={
                            "error_code": "PRODUCT_NOT_FOUND", "message": "Product not found"})
    if product.is_sold:
        raise HTTPException(status_code=409, detail={
                            "error_code": "PRODUCT_ALREADY_SOLD", "message": "Product already sold"})

    if req.reseller_price < product.minimum_sell_price:
        raise HTTPException(status_code=400, detail={
                            "error_code": "RESELLER_PRICE_TOO_LOW", "message": "Reseller price is below minimum sell price"})

    # Atomically mark as sold
    product.is_sold = True
    db.commit()

    return PurchaseResponse(
        product_id=product.id,
        final_price=req.reseller_price,
        value_type=product.value_type,
        value=product.value
    )

# --- ADMIN API (Minimal CRUD to populate DB) ---


@app.post("/admin/products", status_code=status.HTTP_201_CREATED)
def create_product(req: ProductCreate, db: Session = Depends(get_db)):
    if req.cost_price < 0 or req.margin_percentage < 0:
        raise HTTPException(
            status_code=400, detail="Pricing fields must be positive")

    # Server-side calculation of minimum_sell_price
    min_sell_price = req.cost_price * (1 + req.margin_percentage / 100)

    new_product = ProductDB(
        name=req.name,
        description=req.description,
        image_url=req.image_url,
        cost_price=req.cost_price,
        margin_percentage=req.margin_percentage,
        minimum_sell_price=min_sell_price,
        value_type=req.value_type,
        value=req.value
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"message": "Product created successfully", "id": new_product.id}

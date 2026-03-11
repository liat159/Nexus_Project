from sqlalchemy.orm import Session
from models import ProductDB
from schemas import ProductCreate, ProductUpdate


class ProductException(Exception):
    def __init__(self, status_code: int, error_code: str, message: str):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message


def create_product(db: Session, req: ProductCreate):
    if req.cost_price < 0 or req.margin_percentage < 0:
        raise ProductException(400, "INVALID_PRICING",
                               "Pricing fields must be positive")

    min_sell_price = req.cost_price * (1 + req.margin_percentage / 100)
    new_product = ProductDB(
        name=req.name, description=req.description, image_url=req.image_url,
        cost_price=req.cost_price, margin_percentage=req.margin_percentage,
        minimum_sell_price=min_sell_price, value_type=req.value_type, value=req.value
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def get_available_products(db: Session):
    return db.query(ProductDB).filter(ProductDB.is_sold == False).all()


def purchase_reseller(db: Session, product_id: str, reseller_price: float):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise ProductException(404, "PRODUCT_NOT_FOUND", "Product not found")
    if product.is_sold:
        raise ProductException(
            409, "PRODUCT_ALREADY_SOLD", "Product already sold")
    if reseller_price < product.minimum_sell_price:
        raise ProductException(400, "RESELLER_PRICE_TOO_LOW",
                               "Price is below minimum sell price")

    product.is_sold = True
    db.commit()
    return product


def purchase_direct(db: Session, product_id: str):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise ProductException(404, "PRODUCT_NOT_FOUND", "Product not found")
    if product.is_sold:
        raise ProductException(
            409, "PRODUCT_ALREADY_SOLD", "Product already sold")

    product.is_sold = True
    db.commit()
    return product

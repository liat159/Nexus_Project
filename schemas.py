from pydantic import BaseModel
from typing import Optional
from models import ProductType, ValueType


class ProductCreate(BaseModel):
    name: str
    description: str
    image_url: str
    cost_price: float
    margin_percentage: float
    value_type: ValueType
    value: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    cost_price: Optional[float] = None
    margin_percentage: Optional[float] = None
    value_type: Optional[ValueType] = None
    value: Optional[str] = None


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

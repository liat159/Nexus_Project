from sqlalchemy import Column, String, Float, Boolean, DateTime, Enum as SQLEnum
import enum
import uuid
from datetime import datetime
from database import Base


class ProductType(enum.Enum):
    COUPON = "COUPON"


class ValueType(enum.Enum):
    STRING = "STRING"
    IMAGE = "IMAGE"


class ProductDB(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True,
                default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(SQLEnum(ProductType), default=ProductType.COUPON)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    cost_price = Column(Float, nullable=False)
    margin_percentage = Column(Float, nullable=False)
    minimum_sell_price = Column(Float, nullable=False)
    is_sold = Column(Boolean, default=False)

    value_type = Column(SQLEnum(ValueType), nullable=False)
    value = Column(String, nullable=False)

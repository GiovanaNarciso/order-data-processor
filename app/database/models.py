from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    orders = relationship(
        "OrderModel",
        back_populates="user",
        cascade="all," "delete-orphan"
        )


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)

    user = relationship("UserModel", back_populates="orders")
    products = relationship(
        "ProductModel",
        back_populates="order",
        cascade="all, delete-orphan"
        )


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    value = Column(Float, nullable=False)

    order = relationship("OrderModel", back_populates="products")

from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass(frozen=True)
class Product:
    product_id: int
    value: float


@dataclass
class Order:
    order_id: int
    date: date
    products: List[Product] = field(default_factory=list)

    @property
    def total(self) -> float:
        return round(sum(p.value for p in self.products), 2)

    def add_product(self, product: Product):
        self.products.append(product)


@dataclass
class User:
    user_id: int
    name: str
    orders: List[Order] = field(default_factory=list)

    def add_order(self, order: Order):
        self.orders.append(order)

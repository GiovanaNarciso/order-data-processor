from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
from app.domain.models import User
from app.database.models import UserModel, OrderModel, ProductModel


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def save_users(self, users: List[User]) -> None:
        for user in users:
            db_user = (
                self.db.query(UserModel)
                .filter_by(id=user.user_id)
                .first()
            )
            if not db_user:
                db_user = UserModel(id=user.user_id, name=user.name)
                self.db.add(db_user)
                self.db.flush()

            for order in user.orders:
                db_order = (
                    self.db.query(OrderModel)
                    .filter_by(id=order.order_id)
                    .first()
                )
                if not db_order:
                    db_order = OrderModel(
                        id=order.order_id,
                        user_id=db_user.id,
                        date=order.date
                    )
                    self.db.add(db_order)
                    self.db.flush()

                    for product in order.products:
                        db_product = ProductModel(
                            product_id=product.product_id,
                            order_id=db_order.id,
                            value=product.value
                        )
                        self.db.add(db_product)

        self.db.commit()

    def get_orders(
        self,
        order_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ):
        query = self.db.query(UserModel).join(OrderModel).join(ProductModel)

        if order_id:
            query = query.filter(OrderModel.id == order_id)
        if start_date:
            query = query.filter(
                OrderModel.date >= datetime.strptime(
                    start_date, "%Y-%m-%d"
                    ).date()
            )
        if end_date:
            query = query.filter(
                OrderModel.date <= datetime.strptime(
                    end_date, "%Y-%m-%d"
                    ).date()
            )

        users = query.all()
        result = []

        for user in users:
            user_data = {
                "user_id": user.id,
                "name": user.name,
                "orders": []
            }

            for order in user.orders:
                if order_id and order.id != order_id:
                    continue
                if (
                    start_date
                    and order.date < datetime.strptime(start_date, "%Y-%m-%d"
                                                       ).date()
                ):
                    continue
                if (
                    end_date
                    and order.date > datetime.strptime(end_date, "%Y-%m-%d"
                                                       ).date()
                ):
                    continue

                order_data = {
                    "order_id": order.id,
                    "total": f"{sum(p.value for p in order.products):.2f}",
                    "date": order.date.strftime("%Y-%m-%d"),
                    "products": [
                        {
                            "product_id": p.product_id,
                            "value": f"{p.value:.2f}"
                        }
                        for p in order.products
                    ]
                }

                user_data["orders"].append(order_data)

            if user_data["orders"]:
                result.append(user_data)

        return result

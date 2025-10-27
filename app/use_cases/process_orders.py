from typing import List, Optional
from datetime import date
from app.domain.models import User
from app.adapters.file_reader import FileReader


class OrderProcessor:
    def __init__(self, file_reader: FileReader):
        self.file_reader = file_reader

    def execute(
        self,
        order_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[User]:
        users = self.file_reader.parse_file()
        result = []

        for user in users:
            filtered_orders = []
            for order in user.orders:
                if order_id is not None and order.order_id != order_id:
                    continue
                if start_date and order.date < start_date:
                    continue
                if end_date and order.date > end_date:
                    continue
                filtered_orders.append(order)

            if filtered_orders:
                result.append(User(
                    user_id=user.user_id,
                    name=user.name,
                    orders=filtered_orders
                ))

        return result

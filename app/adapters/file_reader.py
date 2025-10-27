from fastapi import HTTPException
from datetime import datetime
from typing import List, Dict
from app.domain.models import User, Order, Product


class FileReader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse_file(self) -> List[User]:
        users_dict: Dict[int, User] = {}

        with open(self.file_path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, start=1):
                if len(line.strip()) < 95:
                    raise HTTPException(
                        status_code=422,
                        detail=(
                            f"Line {line_number} is incomplete or malformed."
                        )
                    )

                try:
                    user_id = int(line[0:10])
                    name = line[10:55].strip()
                    order_id = int(line[55:65])
                    product_id = int(line[65:75])
                    value = float(line[75:87].strip())
                    raw_date = line[87:95].strip()
                    date_obj = datetime.strptime(raw_date, "%Y%m%d").date()
                except Exception as e:
                    raise HTTPException(
                        status_code=422,
                        detail=f"Failed to parse line {line_number}: {str(e)}"
                    )

                product = Product(product_id=product_id, value=value)

                user = users_dict.get(user_id)
                if not user:
                    user = User(user_id=user_id, name=name)
                    users_dict[user_id] = user

                order = next(
                    (o for o in user.orders if o.order_id == order_id),
                    None
                )
                if not order:
                    order = Order(order_id=order_id, date=date_obj)
                    user.add_order(order)

                order.add_product(product)

        return list(users_dict.values())

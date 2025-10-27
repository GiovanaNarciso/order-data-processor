from datetime import date
from unittest.mock import MagicMock

from app.use_cases.order_service import OrderService
from app.domain.models import User, Order, Product
from app.database.models import UserModel, OrderModel, ProductModel


def test_save_users_creates_all_models():
    db = MagicMock()
    db.query().filter_by().first.return_value = None

    user = User(user_id=1, name="Giovana")
    order = Order(order_id=10, date=date(2025, 5, 10))
    order.add_product(Product(product_id=100, value=200.0))
    user.add_order(order)

    service = OrderService(db)
    service.save_users([user])

    assert db.add.call_count == 3
    db.commit.assert_called_once()


def test_get_orders_filters_and_formats_result():
    db = MagicMock()

    user_mock = UserModel(id=1, name="Giovana")
    order_mock = OrderModel(id=99, date=date(2025, 5, 16))
    product_mock = ProductModel(product_id=5, value=123.45)

    order_mock.products = [product_mock]
    user_mock.orders = [order_mock]

    db_query = MagicMock()
    db_query.join.return_value = db_query
    db_query.filter.return_value = db_query
    db_query.all.return_value = [user_mock]

    db.query.return_value = db_query

    service = OrderService(db)
    results = service.get_orders(
        order_id=99,
        start_date="2025-01-01",
        end_date="2025-12-31"
    )

    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["user_id"] == 1
    assert results[0]["orders"][0]["order_id"] == 99
    assert results[0]["orders"][0]["total"] == "123.45"
    assert results[0]["orders"][0]["products"][0]["product_id"] == 5

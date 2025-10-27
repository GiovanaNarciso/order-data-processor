import os
from app.adapters.file_reader import FileReader


def get_fixture_file_path(filename: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "fixtures", filename)


def test_user_order_product_structure_from_fixture():
    fixture_path = get_fixture_file_path("sample.txt")
    reader = FileReader(file_path=fixture_path)
    users = reader.parse_file()

    user = next(u for u in users if u.user_id == 70)
    assert user.name.strip() == "Palmer Prosacco"
    assert len(user.orders) == 2

    order = next(o for o in user.orders if o.order_id == 753)
    assert order.total == 1836.74
    assert len(order.products) == 1

    product = order.products[0]
    assert product.product_id == 3
    assert product.value == 1836.74

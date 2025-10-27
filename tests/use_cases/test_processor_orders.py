import os
from datetime import date
from app.use_cases.process_orders import OrderProcessor
from app.adapters.file_reader import FileReader


def get_fixture_file_path(filename: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "fixtures", filename)


def get_processor_from_fixture() -> OrderProcessor:
    fixture_path = get_fixture_file_path("sample.txt")
    reader = FileReader(file_path=fixture_path)
    return OrderProcessor(file_reader=reader)


def test_filter_by_order_id():
    processor = get_processor_from_fixture()
    result = processor.execute(order_id=753)

    assert len(result) == 1
    assert result[0].user_id == 70
    assert len(result[0].orders) == 1
    assert result[0].orders[0].order_id == 753


def test_filter_by_date_range():
    processor = get_processor_from_fixture()
    result = processor.execute(
        start_date=date(2021, 9, 1),
        end_date=date(2021, 12, 31)
    )

    assert len(result) == 4
    assert all(
        all(date(2021, 9, 1) <= o.date <= date(2021, 12, 31) for o in u.orders)
        for u in result
    )


def test_returns_empty_list_when_no_order_matches_filters():
    processor = get_processor_from_fixture()
    result = processor.execute(
        order_id=999999,
        start_date=date(2100, 1, 1),
        end_date=date(2100, 12, 31)
    )
    assert result == []

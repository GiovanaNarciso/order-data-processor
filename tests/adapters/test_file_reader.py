import os
import pytest
from fastapi import HTTPException
from app.adapters.file_reader import FileReader


def test_file_reader_parses_sample_fixture():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    fixture_path = os.path.join(base_dir, "fixtures", "sample.txt")

    reader = FileReader(file_path=fixture_path)
    users = reader.parse_file()

    assert len(users) == 4

    user_map = {u.user_id: u for u in users}

    user70 = user_map[70]
    assert user70.name.strip() == "Palmer Prosacco"
    assert len(user70.orders) == 2
    assert sorted(o.order_id for o in user70.orders) == [620, 753]


def test_file_reader_raises_on_malformed_line():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    fixture_path = os.path.join(base_dir, "fixtures", "invalid_sample.txt")

    reader = FileReader(file_path=fixture_path)

    with pytest.raises(HTTPException) as exc_info:
        reader.parse_file()

    assert exc_info.value.status_code == 422
    assert "Line 1 is incomplete or malformed." in str(exc_info.value.detail)

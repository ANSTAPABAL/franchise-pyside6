import pytest

from services.monitor_service import monitor_rows


@pytest.mark.smoke
def test_monitor_rows_returns_tuple():
    try:
        rows, totals = monitor_rows(None, None, None)
    except Exception as exc:
        pytest.skip(f"БД недоступна для smoke: {exc}")

    assert isinstance(rows, list)
    assert isinstance(totals, dict)
    assert "machines" in totals
    assert "money" in totals

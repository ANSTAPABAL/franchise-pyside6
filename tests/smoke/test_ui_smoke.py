import pytest

from app.widgets.sidebar import Sidebar


@pytest.mark.smoke
def test_sidebar_can_toggle_admin(qtbot):
    sidebar = Sidebar()
    qtbot.addWidget(sidebar)
    sidebar.show()
    assert sidebar.admin_group.isVisibleTo(sidebar) is False
    sidebar.admin_root_btn.click()
    assert sidebar.admin_group.isVisibleTo(sidebar) is True
    sidebar.admin_root_btn.click()
    assert sidebar.admin_group.isVisibleTo(sidebar) is False

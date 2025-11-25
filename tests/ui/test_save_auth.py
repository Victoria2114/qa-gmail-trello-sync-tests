import pytest
from playwright.sync_api import Page



BOARD_URL = "https://trello.com/b/OPIvELsg/droxi-ui-test"

@pytest.mark.skip(reason="Auth state already saved, helper test disabled")
@pytest.mark.ui
def test_save_trello_auth_state(page: Page):
    """
    One-time helper test:
    1. Opens the Droxi Trello board.
    2. You manually log in.
    3. After login, the test saves auth_state.json for future UI tests.
    """
    page.goto(BOARD_URL)

    # Give yourself time to complete Google login manually
    page.wait_for_timeout(120000)  # 120 seconds

    # After you are logged in and see the board, auth state will be saved:
    page.context.storage_state(path="auth_state.json")

import os
import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "api: mark API tests")
    config.addinivalue_line("markers", "ui: mark UI tests")

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    If auth_state.json exists, reuse it so all UI tests run as an already
    logged-in Trello user. If it doesn't exist yet, run without it.
    """
    if os.path.exists("auth_state.json"):
        return {**browser_context_args, "storage_state": "auth_state.json"}
    return browser_context_args
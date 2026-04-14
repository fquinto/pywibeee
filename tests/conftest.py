"""Global test configuration for pywibeee."""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests.

    The enable_custom_integrations fixture is provided by
    pytest-homeassistant-custom-component and is REQUIRED for
    custom components to be loadable during tests.
    """
    yield

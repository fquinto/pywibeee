"""Tests for the WibeeeAPI client."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from pywibeee import WibeeeAPI


def _make_api() -> WibeeeAPI:
    return WibeeeAPI(MagicMock(), "192.168.1.150")


def _mock_discovery(api: WibeeeAPI) -> None:
    """Mock the discovery requests with instant successful responses."""
    api.async_fetch_status = AsyncMock(
        return_value={"model": "WBT", "webversion": "4.4.199"}
    )
    api._fetch_device_id = AsyncMock(return_value="WIBEEE")
    api._fetch_mac_address = AsyncMock(return_value="00:1e:c0:11:22:33")


async def test_device_info_within_deadline() -> None:
    """A responsive device returns info well within the default deadline."""
    api = _make_api()
    _mock_discovery(api)

    info = await api.async_fetch_device_info()

    assert info is not None
    assert info.mac_addr_formatted == "001ec0112233"
    assert info.model == "WBT"
    assert info.firmware_version == "4.4.199"


async def test_device_info_deadline_exceeded() -> None:
    """An unresponsive device raises TimeoutError at the overall deadline."""
    api = _make_api()

    async def hang(url: str, retries: int = 0) -> str | None:
        await asyncio.sleep(30)
        return None

    api.async_fetch_url = hang

    with pytest.raises(asyncio.TimeoutError):
        await api.async_fetch_device_info(deadline=0.05)


async def test_device_info_deadline_disabled() -> None:
    """deadline=None disables the overall bound."""
    api = _make_api()
    _mock_discovery(api)

    info = await api.async_fetch_device_info(deadline=None)

    assert info is not None
    assert info.wibeee_id == "WIBEEE"

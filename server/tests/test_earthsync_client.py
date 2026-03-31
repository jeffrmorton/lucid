"""Tests for EarthSync API client."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from lucid_server.services.earthsync_client import EarthSyncClient


def test_init_defaults() -> None:
    """Default station_id and base_url stored correctly."""
    client = EarthSyncClient("http://localhost:3001")
    assert client._base_url == "http://localhost:3001"
    assert client._station_id == "simulator1"


def test_init_strips_trailing_slash() -> None:
    """Trailing slash on base_url is stripped."""
    client = EarthSyncClient("http://localhost:3001/")
    assert client._base_url == "http://localhost:3001"


def test_current_frequency_default() -> None:
    """Returns 7.83 Hz before any fetch."""
    client = EarthSyncClient("http://localhost:3001")
    assert client.current_frequency == 7.83


def test_station_id_property() -> None:
    """Returns configured station_id."""
    client = EarthSyncClient("http://localhost:3001")
    assert client.station_id == "simulator1"


def test_custom_station_id() -> None:
    """Non-default station_id works."""
    client = EarthSyncClient("http://localhost:3001", station_id="station_alpha")
    assert client.station_id == "station_alpha"


@pytest.mark.asyncio
async def test_fetch_success() -> None:
    """Mock httpx returns valid data -- freq/amp updated."""
    client = EarthSyncClient("http://localhost:3001")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"peaks": [{"freq": 7.85, "amp": 1.2, "q_factor": 5.0}]}

    mock_async_client = AsyncMock()
    mock_async_client.get = AsyncMock(return_value=mock_response)
    mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
    mock_async_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "lucid_server.services.earthsync_client.httpx.AsyncClient", return_value=mock_async_client
    ):
        result = await client.fetch_sr_state()

    assert result["freq"] == 7.85
    assert result["amp"] == 1.2
    assert result["q_factor"] == 5.0
    assert client.current_frequency == 7.85


@pytest.mark.asyncio
async def test_fetch_with_peaks_selects_lowest() -> None:
    """Multiple peaks -- selects lowest frequency (mode 1)."""
    client = EarthSyncClient("http://localhost:3001")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "peaks": [
            {"freq": 14.3, "amp": 0.5, "q_factor": 3.0},
            {"freq": 7.81, "amp": 1.5, "q_factor": 6.0},
            {"freq": 20.8, "amp": 0.3, "q_factor": 2.0},
        ]
    }

    mock_async_client = AsyncMock()
    mock_async_client.get = AsyncMock(return_value=mock_response)
    mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
    mock_async_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "lucid_server.services.earthsync_client.httpx.AsyncClient", return_value=mock_async_client
    ):
        result = await client.fetch_sr_state()

    assert result["freq"] == 7.81
    assert result["amp"] == 1.5
    assert result["q_factor"] == 6.0


@pytest.mark.asyncio
async def test_fetch_empty_peaks() -> None:
    """No peaks in response -- returns fallback values."""
    client = EarthSyncClient("http://localhost:3001")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"peaks": []}

    mock_async_client = AsyncMock()
    mock_async_client.get = AsyncMock(return_value=mock_response)
    mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
    mock_async_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "lucid_server.services.earthsync_client.httpx.AsyncClient", return_value=mock_async_client
    ):
        result = await client.fetch_sr_state()

    assert result["freq"] == 7.83
    assert result["amp"] == 0.0
    assert result["q_factor"] is None


@pytest.mark.asyncio
async def test_fetch_http_error() -> None:
    """Non-200 status -- returns fallback values."""
    client = EarthSyncClient("http://localhost:3001")

    mock_response = MagicMock()
    mock_response.status_code = 500

    mock_async_client = AsyncMock()
    mock_async_client.get = AsyncMock(return_value=mock_response)
    mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
    mock_async_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "lucid_server.services.earthsync_client.httpx.AsyncClient", return_value=mock_async_client
    ):
        result = await client.fetch_sr_state()

    assert result["freq"] == 7.83
    assert result["q_factor"] is None


@pytest.mark.asyncio
async def test_fetch_network_error() -> None:
    """httpx raises -- returns fallback, logs warning."""
    client = EarthSyncClient("http://localhost:3001")

    mock_async_client = AsyncMock()
    mock_async_client.get = AsyncMock(side_effect=httpx.ConnectError("connection refused"))
    mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
    mock_async_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "lucid_server.services.earthsync_client.httpx.AsyncClient", return_value=mock_async_client
    ):
        with patch("lucid_server.services.earthsync_client.logger") as mock_logger:
            result = await client.fetch_sr_state()
            mock_logger.warning.assert_called_once()

    assert result["freq"] == 7.83
    assert result["q_factor"] is None


@pytest.mark.asyncio
async def test_fetch_updates_last_known() -> None:
    """After successful fetch, current_frequency reflects new value."""
    client = EarthSyncClient("http://localhost:3001")
    assert client.current_frequency == 7.83

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"peaks": [{"freq": 7.90, "amp": 2.0}]}

    mock_async_client = AsyncMock()
    mock_async_client.get = AsyncMock(return_value=mock_response)
    mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
    mock_async_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "lucid_server.services.earthsync_client.httpx.AsyncClient", return_value=mock_async_client
    ):
        await client.fetch_sr_state()

    assert client.current_frequency == 7.90

    # Now simulate a failure -- should retain last known value
    mock_async_client2 = AsyncMock()
    mock_async_client2.get = AsyncMock(side_effect=httpx.ConnectError("fail"))
    mock_async_client2.__aenter__ = AsyncMock(return_value=mock_async_client2)
    mock_async_client2.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "lucid_server.services.earthsync_client.httpx.AsyncClient", return_value=mock_async_client2
    ):
        result = await client.fetch_sr_state()

    assert result["freq"] == 7.90
    assert client.current_frequency == 7.90


@pytest.mark.asyncio
async def test_fetch_missing_freq_in_peak() -> None:
    """Peak without freq key falls back to 7.83."""
    client = EarthSyncClient("http://localhost:3001")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"peaks": [{"amp": 1.0, "q_factor": 4.0}]}

    mock_async_client = AsyncMock()
    mock_async_client.get = AsyncMock(return_value=mock_response)
    mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
    mock_async_client.__aexit__ = AsyncMock(return_value=False)

    with patch(
        "lucid_server.services.earthsync_client.httpx.AsyncClient", return_value=mock_async_client
    ):
        result = await client.fetch_sr_state()

    # min() with key=lambda p: p.get("freq", 999) will pick 999,
    # then mode1.get("freq", 7.83) falls back to 7.83
    assert result["freq"] == 7.83
    assert result["amp"] == 1.0

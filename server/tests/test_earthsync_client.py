"""Tests for EarthSync API client."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from lucid_server.services.earthsync_client import EarthSyncClient


def _mock_client(get_mock: AsyncMock) -> AsyncMock:
    """Build a mock httpx.AsyncClient with the given get() behaviour."""
    mock = AsyncMock()
    mock.get = get_mock
    mock.aclose = AsyncMock()
    return mock


def _patch_async_client(mock: AsyncMock):
    return patch("lucid_server.services.earthsync_client.httpx.AsyncClient", return_value=mock)


def test_init_defaults() -> None:
    """Default station_id and base_url stored correctly."""
    client = EarthSyncClient("http://localhost:8000")
    assert client._base_url == "http://localhost:8000"
    assert client._station_id == "simulator1"
    assert client.degraded is False


def test_init_strips_trailing_slash() -> None:
    """Trailing slash on base_url is stripped."""
    client = EarthSyncClient("http://localhost:8000/")
    assert client._base_url == "http://localhost:8000"


def test_init_rejects_bad_scheme() -> None:
    """Non-http(s) base_url is rejected (SSRF allowlist)."""
    with pytest.raises(ValueError, match="Unsupported EarthSync URL"):
        EarthSyncClient("file:///etc/passwd")


def test_init_rejects_missing_host() -> None:
    """base_url without a host is rejected."""
    with pytest.raises(ValueError, match="Unsupported EarthSync URL"):
        EarthSyncClient("http://")


def test_init_rejects_bad_station_id() -> None:
    """station_id with path-traversal characters is rejected."""
    with pytest.raises(ValueError, match="Invalid station_id"):
        EarthSyncClient("http://localhost:8000", station_id="../../etc/passwd")


def test_current_frequency_default() -> None:
    """Returns 7.83 Hz before any fetch."""
    client = EarthSyncClient("http://localhost:8000")
    assert client.current_frequency == 7.83


def test_station_id_property() -> None:
    """Returns configured station_id."""
    client = EarthSyncClient("http://localhost:8000")
    assert client.station_id == "simulator1"


def test_custom_station_id() -> None:
    """Non-default station_id works."""
    client = EarthSyncClient("http://localhost:8000", station_id="station_alpha")
    assert client.station_id == "station_alpha"


@pytest.mark.asyncio
async def test_fetch_success() -> None:
    """Mock httpx returns valid data -- freq/amp updated."""
    client = EarthSyncClient("http://localhost:8000")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"peaks": [{"freq": 7.85, "amp": 1.2, "q_factor": 5.0}]}

    mock = _mock_client(AsyncMock(return_value=mock_response))
    with _patch_async_client(mock):
        result = await client.fetch_sr_state()

    assert result["freq"] == 7.85
    assert result["amp"] == 1.2
    assert result["q_factor"] == 5.0
    assert client.current_frequency == 7.85
    assert client.degraded is False


@pytest.mark.asyncio
async def test_fetch_selects_closest_to_fundamental() -> None:
    """Multiple in-band peaks -- selects the one closest to 7.83 Hz."""
    client = EarthSyncClient("http://localhost:8000")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "peaks": [
            {"freq": 14.3, "amp": 0.5, "q_factor": 3.0},  # out of band (mode 2)
            {"freq": 8.9, "amp": 0.4, "q_factor": 4.0},  # in band, farther
            {"freq": 7.81, "amp": 1.5, "q_factor": 6.0},  # in band, closest
            {"freq": 20.8, "amp": 0.3, "q_factor": 2.0},  # out of band
        ]
    }

    mock = _mock_client(AsyncMock(return_value=mock_response))
    with _patch_async_client(mock):
        result = await client.fetch_sr_state()

    assert result["freq"] == 7.81
    assert result["amp"] == 1.5
    assert result["q_factor"] == 6.0


@pytest.mark.asyncio
async def test_fetch_ignores_sub_fundamental_peak() -> None:
    """A spurious low-frequency peak (e.g. 3 Hz) is NOT treated as the fundamental."""
    client = EarthSyncClient("http://localhost:8000")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"peaks": [{"freq": 3.0, "amp": 9.0}]}

    mock = _mock_client(AsyncMock(return_value=mock_response))
    with (
        _patch_async_client(mock),
        patch("lucid_server.services.earthsync_client.logger") as mock_logger,
    ):
        result = await client.fetch_sr_state()
        mock_logger.warning.assert_called_once()

    assert result["freq"] == 7.83  # fell back to canonical fundamental
    assert client.degraded is True


@pytest.mark.asyncio
async def test_fetch_empty_peaks() -> None:
    """No peaks in response -- returns fallback values and logs a warning."""
    client = EarthSyncClient("http://localhost:8000")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"peaks": []}

    mock = _mock_client(AsyncMock(return_value=mock_response))
    with (
        _patch_async_client(mock),
        patch("lucid_server.services.earthsync_client.logger") as mock_logger,
    ):
        result = await client.fetch_sr_state()
        mock_logger.warning.assert_called_once()

    assert result["freq"] == 7.83
    assert result["amp"] == 0.0
    assert result["q_factor"] is None
    assert client.degraded is True


@pytest.mark.asyncio
async def test_fetch_http_error() -> None:
    """Non-200 status -- returns fallback values, logs warning, sets degraded."""
    client = EarthSyncClient("http://localhost:8000")

    mock_response = MagicMock()
    mock_response.status_code = 500

    mock = _mock_client(AsyncMock(return_value=mock_response))
    with (
        _patch_async_client(mock),
        patch("lucid_server.services.earthsync_client.logger") as mock_logger,
    ):
        result = await client.fetch_sr_state()
        mock_logger.warning.assert_called_once()

    assert result["freq"] == 7.83
    assert result["q_factor"] is None
    assert client.degraded is True


@pytest.mark.asyncio
async def test_fetch_network_error() -> None:
    """httpx raises -- returns fallback, logs warning."""
    client = EarthSyncClient("http://localhost:8000")

    mock = _mock_client(AsyncMock(side_effect=httpx.ConnectError("connection refused")))
    with (
        _patch_async_client(mock),
        patch("lucid_server.services.earthsync_client.logger") as mock_logger,
    ):
        result = await client.fetch_sr_state()
        mock_logger.warning.assert_called_once()

    assert result["freq"] == 7.83
    assert result["q_factor"] is None
    assert client.degraded is True


@pytest.mark.asyncio
async def test_fetch_reuses_single_client() -> None:
    """The httpx.AsyncClient is constructed once and reused across polls."""
    client = EarthSyncClient("http://localhost:8000")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"peaks": [{"freq": 7.83, "amp": 1.0}]}

    mock = _mock_client(AsyncMock(return_value=mock_response))
    with _patch_async_client(mock) as ctor:
        await client.fetch_sr_state()
        await client.fetch_sr_state()
        assert ctor.call_count == 1  # constructed once, reused


@pytest.mark.asyncio
async def test_aclose_closes_client() -> None:
    """aclose() closes the underlying client and is safe to call when unused."""
    client = EarthSyncClient("http://localhost:8000")
    # No fetch yet -> no client -> aclose is a no-op.
    await client.aclose()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"peaks": [{"freq": 7.83, "amp": 1.0}]}
    mock = _mock_client(AsyncMock(return_value=mock_response))
    with _patch_async_client(mock):
        await client.fetch_sr_state()
        await client.aclose()
        mock.aclose.assert_awaited_once()
    assert client._client is None


@pytest.mark.asyncio
async def test_fetch_updates_last_known() -> None:
    """After successful fetch, current_frequency reflects new value."""
    client = EarthSyncClient("http://localhost:8000")
    assert client.current_frequency == 7.83

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"peaks": [{"freq": 7.90, "amp": 2.0}]}

    mock = _mock_client(AsyncMock(return_value=mock_response))
    with _patch_async_client(mock):
        await client.fetch_sr_state()

    assert client.current_frequency == 7.90

    # Now simulate a failure -- should retain last known value
    mock2 = _mock_client(AsyncMock(side_effect=httpx.ConnectError("fail")))
    with _patch_async_client(mock2):
        result = await client.fetch_sr_state()

    assert result["freq"] == 7.90
    assert client.current_frequency == 7.90


@pytest.mark.asyncio
async def test_fetch_missing_freq_in_peak() -> None:
    """Peak without freq key is out-of-band -> falls back to 7.83."""
    client = EarthSyncClient("http://localhost:8000")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"peaks": [{"amp": 1.0, "q_factor": 4.0}]}

    mock = _mock_client(AsyncMock(return_value=mock_response))
    with _patch_async_client(mock):
        result = await client.fetch_sr_state()

    assert result["freq"] == 7.83
    assert client.degraded is True

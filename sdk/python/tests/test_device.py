"""Tests for Lucid SDK device module."""

from lucid.device import LucidDevice


def test_device_creation() -> None:
    device = LucidDevice()
    assert not device.connected
    assert device.sample_rate == 250
    assert device.n_channels == 8


def test_device_connect() -> None:
    device = LucidDevice()
    assert device.connect()
    assert device.is_connected()


def test_device_disconnect() -> None:
    device = LucidDevice()
    device.connect()
    device.disconnect()
    assert not device.is_connected()


def test_device_with_address() -> None:
    device = LucidDevice(address="AA:BB:CC:DD:EE:FF")
    assert device.address == "AA:BB:CC:DD:EE:FF"

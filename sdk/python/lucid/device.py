"""Device connection and data streaming."""


class LucidDevice:
    """Interface to a Lucid BCI device via BLE or WiFi."""

    def __init__(self, address: str | None = None) -> None:
        self.address = address
        self.connected = False
        self.sample_rate = 250
        self.n_channels = 8

    def connect(self) -> bool:
        """Connect to the device."""
        # TODO: Implement BLE/WiFi connection
        self.connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from the device."""
        self.connected = False

    def is_connected(self) -> bool:
        """Check if device is connected."""
        return self.connected

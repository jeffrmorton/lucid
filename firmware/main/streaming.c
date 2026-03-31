/* BLE and WiFi streaming implementation */
#include "streaming.h"

bool streaming_init_ble(void) {
    // TODO: Initialize BLE GATT server
    return true;
}

bool streaming_init_wifi(const char *ssid, const char *password) {
    // TODO: Initialize WiFi + WebSocket/WebTransport
    return true;
}

void streaming_send(const int32_t *channels, int n_channels) {
    // TODO: Send sample via BLE notification or WebSocket
}

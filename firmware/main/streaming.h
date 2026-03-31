/* BLE and WiFi data streaming */
#pragma once
#include <stdbool.h>
#include <stdint.h>

bool streaming_init_ble(void);
bool streaming_init_wifi(const char *ssid, const char *password);
void streaming_send(const int32_t *channels, int n_channels);

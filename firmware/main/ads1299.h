/* ADS1299 SPI driver for ESP32-S3 */
#pragma once
#include <stdint.h>
#include <stdbool.h>

#define ADS1299_CHANNELS 8
#define ADS1299_SAMPLE_RATE 250

bool ads1299_init(int cs_pin, int drdy_pin, int reset_pin);
void ads1299_configure(int sample_rate, int gain);
void ads1299_start(void);
void ads1299_stop(void);
bool ads1299_read_sample(int32_t *channels, int n_channels);

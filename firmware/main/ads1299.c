/* ADS1299 SPI driver implementation */
#include "ads1299.h"

bool ads1299_init(int cs_pin, int drdy_pin, int reset_pin) {
    // TODO: Initialize SPI, configure GPIO
    return true;
}

void ads1299_configure(int sample_rate, int gain) {
    // TODO: Write ADS1299 configuration registers
}

void ads1299_start(void) {
    // TODO: Send START command
}

void ads1299_stop(void) {
    // TODO: Send STOP command
}

bool ads1299_read_sample(int32_t *channels, int n_channels) {
    // TODO: Read sample data via SPI
    return true;
}

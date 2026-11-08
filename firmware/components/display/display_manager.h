#pragma once

#include <cstdint>
#include <string>

#define I2C_PIN_SDA 4
#define I2C_PIN_SCL 5

enum class DisplayState {
    IDLE,
    RECORDING,
    MUTED,
    USB_SYNC,
    LOW_BATTERY
};

class DisplayManager {
public:
    DisplayManager();
    bool init();
    void updateState(DisplayState state, uint32_t recordSeconds = 0, uint8_t batteryPct = 100, uint64_t freeStorageMB = 0);
    void setDimmed(bool dim);

private:
    DisplayState _currentState;
    bool _isDimmed;
    void renderScreen(uint32_t recordSeconds, uint8_t batteryPct, uint64_t freeStorageMB);
};


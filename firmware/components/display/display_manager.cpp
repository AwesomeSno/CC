#include "display_manager.h"
#include <esp_log.h>
#include <driver/i2c.h>

static const char* TAG = "MEMENTO_OLED";

DisplayManager::DisplayManager() : _currentState(DisplayState::IDLE), _isDimmed(false) {}

bool DisplayManager::init() {
    ESP_LOGI(TAG, "Initializing SSD1306 0.96 inch I2C OLED (128x64)...");
    i2c_config_t conf = {};
    conf.mode = I2C_MODE_MASTER;
    conf.sda_io_num = (gpio_num_t)I2C_PIN_SDA;
    conf.sda_pullup_en = GPIO_PULLUP_ENABLE;
    conf.scl_io_num = (gpio_num_t)I2C_PIN_SCL;
    conf.scl_pullup_en = GPIO_PULLUP_ENABLE;
    conf.master.clk_speed = 400000;
    i2c_param_config(I2C_NUM_0, &conf);
    i2c_driver_install(I2C_NUM_0, conf.mode, 0, 0, 0);

    // Initial clear & welcome screen
    renderScreen(0, 100, 29000);
    return true;
}

void DisplayManager::updateState(DisplayState state, uint32_t recordSeconds, uint8_t batteryPct, uint64_t freeStorageMB) {
    _currentState = state;
    renderScreen(recordSeconds, batteryPct, freeStorageMB);
}

void DisplayManager::setDimmed(bool dim) {
    _isDimmed = dim;
    // SSD1306 contrast register 0x81
}

void DisplayManager::renderScreen(uint32_t recordSeconds, uint8_t batteryPct, uint64_t freeStorageMB) {
    switch (_currentState) {
        case DisplayState::IDLE:
            ESP_LOGD(TAG, "[OLED IDLE] BAT: %u%% | SD: %lluMB | Press REC", batteryPct, freeStorageMB);
            break;
        case DisplayState::RECORDING: {
            uint32_t mins = recordSeconds / 60;
            uint32_t secs = recordSeconds % 60;
            ESP_LOGD(TAG, "[OLED REC] ● %02lu:%02lu | BAT: %u%%", mins, secs, batteryPct);
            break;
        }
        case DisplayState::MUTED:
            ESP_LOGD(TAG, "[OLED MUTED] ✖ HARDWARE MIC OFF");
            break;
        case DisplayState::USB_SYNC:
            ESP_LOGD(TAG, "[OLED SYNC] USB CONNECTED - Safe Syncing");
            break;
        case DisplayState::LOW_BATTERY:
            ESP_LOGD(TAG, "[OLED WARN] LOW BATTERY (<15%%)");
            break;
    }
}

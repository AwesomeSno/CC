#include "haptics_manager.h"
#include <esp_log.h>
#include <driver/gpio.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

static const char* TAG = "MEMENTO_HAPTIC";

HapticsManager::HapticsManager() {}

bool HapticsManager::init() {
    gpio_config_t io_conf = {};
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pin_bit_mask = (1ULL << PIN_HAPTIC_PWM);
    io_conf.pull_down_en = GPIO_PULLDOWN_ENABLE;
    gpio_config(&io_conf);
    gpio_set_level((gpio_num_t)PIN_HAPTIC_PWM, 0);
    ESP_LOGI(TAG, "ERM Vibration Motor Driver Initialized on GPIO %d", PIN_HAPTIC_PWM);
    return true;
}

void HapticsManager::pulse(uint32_t durationMs, uint8_t dutyPct) {
    gpio_set_level((gpio_num_t)PIN_HAPTIC_PWM, 1);
    vTaskDelay(pdMS_TO_TICKS(durationMs));
    gpio_set_level((gpio_num_t)PIN_HAPTIC_PWM, 0);
}

void HapticsManager::play(HapticProfile profile) {
    switch (profile) {
        case HapticProfile::REC_START:
            pulse(80);
            break;
        case HapticProfile::REC_STOP:
            pulse(60);
            vTaskDelay(pdMS_TO_TICKS(60));
            pulse(60);
            break;
        case HapticProfile::BOOKMARK_TAG:
            pulse(30);
            break;
        case HapticProfile::MUTE_ACTIVE:
            pulse(350);
            break;
        case HapticProfile::LOW_BATTERY:
            for (int i = 0; i < 3; ++i) {
                pulse(100);
                vTaskDelay(pdMS_TO_TICKS(100));
            }
            break;
    }
}

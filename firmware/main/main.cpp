#include <cstdio>
#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <driver/gpio.h>

#include "audio_manager.h"
#include "storage_manager.h"
#include "display_manager.h"
#include "haptics_manager.h"

static const char* TAG = "MEMENTO_MAIN";

#define PIN_BTN_REC   7
#define PIN_BTN_MARK  8

static AudioManager audioMgr;
static StorageManager storageMgr;
static DisplayManager displayMgr;
static HapticsManager hapticsMgr;

void storage_consumer_task(void* pvParameters) {
    uint8_t buffer[4096];
    size_t itemSize = 0;
    RingbufHandle_t ringBuf = audioMgr.getRingBuffer();

    while (true) {
        if (storageMgr.isSessionActive() && ringBuf) {
            void* data = xRingbufferReceiveUpTo(ringBuf, &itemSize, pdMS_TO_TICKS(100), sizeof(buffer));
            if (data && itemSize > 0) {
                // In production: write itemSize bytes to active WAV chunk
                vRingbufferReturnItem(ringBuf, data);
            }
        } else {
            vTaskDelay(pdMS_TO_TICKS(50));
        }
    }
}

extern "C" void app_main() {
    ESP_LOGI(TAG, "================================================");
    ESP_LOGI(TAG, "MEMENTO v1.0 — Intelligent Personal Audio Companion");
    ESP_LOGI(TAG, "Hack Club Half Life // Open Source Hardware");
    ESP_LOGI(TAG, "================================================");

    // 1. Initialize Hardware Components
    hapticsMgr.init();
    displayMgr.init();
    storageMgr.init();
    audioMgr.init();

    // 2. Configure Buttons
    gpio_config_t btn_conf = {};
    btn_conf.mode = GPIO_MODE_INPUT;
    btn_conf.pin_bit_mask = (1ULL << PIN_BTN_REC) | (1ULL << PIN_BTN_MARK);
    btn_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    gpio_config(&btn_conf);

    // 3. Spawn Storage Consumer Task on Core 0
    xTaskCreatePinnedToCore(storage_consumer_task, "storage_task", 4096, nullptr, 10, nullptr, 0);

    // Ready confirmation
    hapticsMgr.play(HapticProfile::BOOKMARK_TAG);
    ESP_LOGI(TAG, "System Ready. Waiting for user interaction...");

    bool lastRecState = false;
    uint32_t sessionSeconds = 0;

    // 4. Main Event Loop
    while (true) {
        bool recBtnPressed = (gpio_get_level((gpio_num_t)PIN_BTN_REC) == 0);
        bool markBtnPressed = (gpio_get_level((gpio_num_t)PIN_BTN_MARK) == 0);
        bool isMuted = audioMgr.isHardwareMuted();

        if (recBtnPressed && !lastRecState) {
            if (!storageMgr.isSessionActive()) {
                ESP_LOGI(TAG, "Record button pressed -> STARTING SESSION");
                storageMgr.startSession("SESSION_001");
                audioMgr.startRecording();
                hapticsMgr.play(HapticProfile::REC_START);
                displayMgr.updateState(DisplayState::RECORDING, 0, 95, storageMgr.getFreeSpaceMB());
            } else {
                ESP_LOGI(TAG, "Record button pressed -> STOPPING SESSION");
                audioMgr.stopRecording();
                storageMgr.endSession();
                hapticsMgr.play(HapticProfile::REC_STOP);
                displayMgr.updateState(DisplayState::IDLE, 0, 95, storageMgr.getFreeSpaceMB());
            }
            vTaskDelay(pdMS_TO_TICKS(250)); // Simple debounce
        }
        lastRecState = recBtnPressed;

        if (markBtnPressed && storageMgr.isSessionActive()) {
            ESP_LOGI(TAG, "Bookmark button pressed -> TAGGED MOMENT");
            storageMgr.addBookmark("User Marked Moment");
            hapticsMgr.play(HapticProfile::BOOKMARK_TAG);
            vTaskDelay(pdMS_TO_TICKS(250));
        }

        if (storageMgr.isSessionActive()) {
            sessionSeconds++;
            if (isMuted) {
                displayMgr.updateState(DisplayState::MUTED);
            } else {
                displayMgr.updateState(DisplayState::RECORDING, sessionSeconds, 94, storageMgr.getFreeSpaceMB());
            }
        }

        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}


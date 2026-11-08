#include "audio_manager.h"
#include <esp_log.h>
#include <driver/i2s_std.h>
#include <driver/gpio.h>

static const char* TAG = "MEMENTO_AUDIO";
static i2s_chan_handle_t rx_handle = nullptr;

AudioManager::AudioManager() : _isRecording(false), _isMuted(false), _ringBuffer(nullptr), _taskHandle(nullptr) {}

bool AudioManager::init() {
    ESP_LOGI(TAG, "Initializing INMP441 I2S DMA Subsystem...");

    // Configure Mute Sense GPIO with pull-up
    gpio_config_t io_conf = {};
    io_conf.intr_type = GPIO_INTR_ANYEDGE;
    io_conf.pin_bit_mask = (1ULL << PIN_MUTE_SENSE);
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    gpio_config(&io_conf);

    // Create FreeRTOS Byte RingBuffer
    _ringBuffer = xRingbufferCreate(AUDIO_RING_BUF_SIZE, RINGBUF_TYPE_BYTEBUF);
    if (!_ringBuffer) {
        ESP_LOGE(TAG, "Failed to allocate audio RingBuffer");
        return false;
    }

    // Allocate I2S standard RX channel
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    chan_cfg.dma_desc_num = 8;
    chan_cfg.dma_frame_num = 512;
    esp_err_t ret = i2s_new_channel(&chan_cfg, nullptr, &rx_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to create I2S RX channel: %s", esp_err_to_name(ret));
        return false;
    }

    // Configure 16kHz, 16-bit mono standard slot
    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(AUDIO_SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = (gpio_num_t)I2S_PIN_SCK,
            .ws = (gpio_num_t)I2S_PIN_WS,
            .dout = I2S_GPIO_UNUSED,
            .din = (gpio_num_t)I2S_PIN_SD,
            .invert_flags = {
                .mclk_inv = false,
                .bclk_inv = false,
                .ws_inv = false,
            },
        },
    };

    ret = i2s_channel_init_std_mode(rx_handle, &std_cfg);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to init I2S std mode: %s", esp_err_to_name(ret));
        return false;
    }

    // Pin Audio Acquisition Task to Core 1 at priority 24 (Highest)
    xTaskCreatePinnedToCore(audioTask, "memento_audio_task", 4096, this, 24, &_taskHandle, 1);
    ESP_LOGI(TAG, "I2S DMA Audio Subsystem Ready (16kHz 16-bit Mono)");
    return true;
}

bool AudioManager::startRecording() {
    if (_isRecording) return true;
    if (i2s_channel_enable(rx_handle) == ESP_OK) {
        _isRecording = true;
        ESP_LOGI(TAG, "Recording started");
        return true;
    }
    return false;
}

void AudioManager::stopRecording() {
    if (!_isRecording) return;
    _isRecording = false;
    i2s_channel_disable(rx_handle);
    ESP_LOGI(TAG, "Recording stopped");
}

bool AudioManager::isRecording() const {
    return _isRecording;
}

bool AudioManager::isHardwareMuted() const {
    return gpio_get_level((gpio_num_t)PIN_MUTE_SENSE) == 0;
}

RingbufHandle_t AudioManager::getRingBuffer() const {
    return _ringBuffer;
}

void AudioManager::audioTask(void* pvParameters) {
    AudioManager* self = static_cast<AudioManager*>(pvParameters);
    int16_t dma_buffer[AUDIO_CHUNK_SIZE / sizeof(int16_t)];
    size_t bytes_read = 0;

    while (true) {
        if (self->_isRecording && !self->isHardwareMuted()) {
            esp_err_t res = i2s_channel_read(rx_handle, dma_buffer, sizeof(dma_buffer), &bytes_read, pdMS_TO_TICKS(100));
            if (res == ESP_OK && bytes_read > 0) {
                // Push DMA audio chunk into RingBuffer
                BaseType_t ok = xRingbufferSend(self->_ringBuffer, dma_buffer, bytes_read, pdMS_TO_TICKS(50));
                if (ok != pdTRUE) {
                    ESP_LOGW(TAG, "Audio RingBuffer overflow: samples dropped");
                }
            }
        } else {
            vTaskDelay(pdMS_TO_TICKS(20));
        }
    }
}

#pragma once

#include <cstdint>
#include <cstddef>
#include "freertos/FreeRTOS.h"
#include "freertos/ringbuf.h"

// I2S Configuration Pins for INMP441
#define I2S_PIN_SCK     15
#define I2S_PIN_WS      16
#define I2S_PIN_SD      17
#define PIN_MUTE_SENSE  9

#define AUDIO_SAMPLE_RATE    16000
#define AUDIO_BITS_PER_SAMP  16
#define AUDIO_CHANNELS       1
#define AUDIO_CHUNK_SIZE     1024
#define AUDIO_RING_BUF_SIZE  (64 * 1024) // 64KB RingBuffer (2 seconds audio buffer)

class AudioManager {
public:
    AudioManager();
    bool init();
    bool startRecording();
    void stopRecording();
    bool isRecording() const;
    bool isHardwareMuted() const;
    RingbufHandle_t getRingBuffer() const;

    // FreeRTOS Task function
    static void audioTask(void* pvParameters);

private:
    bool _isRecording;
    bool _isMuted;
    RingbufHandle_t _ringBuffer;
    TaskHandle_t _taskHandle;
};

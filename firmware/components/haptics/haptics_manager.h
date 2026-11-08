#pragma once

#include <cstdint>

#define PIN_HAPTIC_PWM 6

enum class HapticProfile {
    REC_START,     // 1x Sharp 80ms buzz
    REC_STOP,      // 2x Quick 60ms taps
    BOOKMARK_TAG,  // 1x Gentle 30ms tap
    MUTE_ACTIVE,   // 1x Long 350ms dull buzz
    LOW_BATTERY    // 3x Warning pulses
};

class HapticsManager {
public:
    HapticsManager();
    bool init();
    void play(HapticProfile profile);

private:
    void pulse(uint32_t durationMs, uint8_t dutyPct = 100);
};


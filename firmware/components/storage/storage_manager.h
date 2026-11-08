#pragma once

#include <cstdint>
#include <cstddef>
#include <string>
#include <vector>
#include "freertos/FreeRTOS.h"
#include "freertos/ringbuf.h"

#define SD_PIN_CS    10
#define SD_PIN_MOSI  11
#define SD_PIN_SCK   12
#define SD_PIN_MISO  13

struct Bookmark {
    uint32_t timestampSeconds;
    std::string label;
};

class StorageManager {
public:
    StorageManager();
    bool init();
    bool startSession(const std::string& sessionId);
    void addBookmark(const std::string& label);
    void endSession();
    bool isSessionActive() const;
    uint64_t getFreeSpaceMB() const;

    // FreeRTOS Consumer Task
    static void storageTask(void* pvParameters);

private:
    bool _isMounted;
    bool _sessionActive;
    std::string _currentSessionId;
    std::string _currentSessionDir;
    uint32_t _chunkIndex;
    uint32_t _sessionStartTime;
    uint32_t _bytesWrittenInChunk;
    std::vector<Bookmark> _bookmarks;
    FILE* _currentWavFile;

    bool openNextWavChunk();
    void closeCurrentWavChunk();
    void writeWavHeader(FILE* f, uint32_t dataBytes);
    void saveMetadataJson();
};


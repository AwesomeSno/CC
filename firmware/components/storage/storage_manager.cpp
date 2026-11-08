#include "storage_manager.h"
#include <esp_log.h>
#include <esp_vfs_fat.h>
#include <sdmmc_cmd.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <cstring>

static const char* TAG = "MEMENTO_STORAGE";
#define MOUNT_POINT "/sdcard"
#define MAX_CHUNK_BYTES (15 * 60 * 16000 * 2) // 15 mins of 16kHz 16-bit mono = ~28.8 MB

StorageManager::StorageManager() : 
    _isMounted(false), _sessionActive(false), _chunkIndex(0), 
    _sessionStartTime(0), _bytesWrittenInChunk(0), _currentWavFile(nullptr) {}

bool StorageManager::init() {
    ESP_LOGI(TAG, "Initializing SPI MicroSD Card Driver...");
    
    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = false,
        .max_files = 5,
        .allocation_unit_size = 16 * 1024
    };

    sdmmc_host_t host = SDSPI_HOST_DEFAULT();
    spi_bus_config_t bus_cfg = {
        .mosi_io_num = SD_PIN_MOSI,
        .miso_io_num = SD_PIN_MISO,
        .sclk_io_num = SD_PIN_SCK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 4096,
    };

    esp_err_t ret = spi_bus_initialize((spi_host_device_t)host.slot, &bus_cfg, SDSPI_DEFAULT_DMA);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to initialize SPI bus for SD");
        return false;
    }

    sdspi_device_config_t slot_config = SDSPI_DEVICE_CONFIG_DEFAULT();
    slot_config.gpio_cs = (gpio_num_t)SD_PIN_CS;
    slot_config.host_id = (spi_host_device_t)host.slot;

    sdmmc_card_t* card;
    ret = esp_vfs_fat_sdspi_mount(MOUNT_POINT, &host, &slot_config, &mount_config, &card);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to mount FAT32 filesystem: %s", esp_err_to_name(ret));
        return false;
    }

    sdmmc_card_print_info(stdout, card);
    _isMounted = true;
    mkdir(MOUNT_POINT "/MEMENTO", 0777);
    mkdir(MOUNT_POINT "/MEMENTO/RECORDINGS", 0777);
    return true;
}

void StorageManager::writeWavHeader(FILE* f, uint32_t dataBytes) {
    uint32_t fileSize = dataBytes + 36;
    uint32_t sampleRate = 16000;
    uint16_t numChannels = 1;
    uint16_t bitsPerSample = 16;
    uint32_t byteRate = sampleRate * numChannels * (bitsPerSample / 8);
    uint16_t blockAlign = numChannels * (bitsPerSample / 8);

    uint8_t header[44] = {
        'R', 'I', 'F', 'F',
        (uint8_t)(fileSize), (uint8_t)(fileSize >> 8), (uint8_t)(fileSize >> 16), (uint8_t)(fileSize >> 24),
        'W', 'A', 'V', 'E',
        'f', 'm', 't', ' ',
        16, 0, 0, 0,
        1, 0,
        (uint8_t)(numChannels), (uint8_t)(numChannels >> 8),
        (uint8_t)(sampleRate), (uint8_t)(sampleRate >> 8), (uint8_t)(sampleRate >> 16), (uint8_t)(sampleRate >> 24),
        (uint8_t)(byteRate), (uint8_t)(byteRate >> 8), (uint8_t)(byteRate >> 16), (uint8_t)(byteRate >> 24),
        (uint8_t)(blockAlign), (uint8_t)(blockAlign >> 8),
        (uint8_t)(bitsPerSample), (uint8_t)(bitsPerSample >> 8),
        'd', 'a', 't', 'a',
        (uint8_t)(dataBytes), (uint8_t)(dataBytes >> 8), (uint8_t)(dataBytes >> 16), (uint8_t)(dataBytes >> 24)
    };
    fseek(f, 0, SEEK_SET);
    fwrite(header, 1, sizeof(header), f);
}

bool StorageManager::openNextWavChunk() {
    closeCurrentWavChunk();
    char filepath[128];
    snprintf(filepath, sizeof(filepath), "%s/audio_%03lu.wav", _currentSessionDir.c_str(), _chunkIndex);
    _currentWavFile = fopen(filepath, "wb");
    if (!_currentWavFile) {
        ESP_LOGE(TAG, "Failed to open WAV chunk: %s", filepath);
        return false;
    }
    // Write placeholder header
    writeWavHeader(_currentWavFile, 0);
    _bytesWrittenInChunk = 0;
    _chunkIndex++;
    return true;
}

void StorageManager::closeCurrentWavChunk() {
    if (_currentWavFile) {
        writeWavHeader(_currentWavFile, _bytesWrittenInChunk);
        fclose(_currentWavFile);
        _currentWavFile = nullptr;
    }
}

bool StorageManager::startSession(const std::string& sessionId) {
    if (!_isMounted) return false;
    _currentSessionId = sessionId;
    _currentSessionDir = MOUNT_POINT "/MEMENTO/RECORDINGS/" + sessionId;
    mkdir(_currentSessionDir.c_str(), 0777);
    _chunkIndex = 0;
    _bookmarks.clear();

    struct timeval tv;
    gettimeofday(&tv, NULL);
    _sessionStartTime = tv.tv_sec;

    _sessionActive = openNextWavChunk();
    saveMetadataJson();
    return _sessionActive;
}

void StorageManager::addBookmark(const std::string& label) {
    if (!_sessionActive) return;
    struct timeval tv;
    gettimeofday(&tv, NULL);
    uint32_t offset = tv.tv_sec - _sessionStartTime;
    _bookmarks.push_back({offset, label});
    saveMetadataJson();
}

void StorageManager::saveMetadataJson() {
    std::string metaPath = _currentSessionDir + "/metadata.json";
    FILE* f = fopen(metaPath.c_str(), "w");
    if (!f) return;
    fprintf(f, "{\n");
    fprintf(f, "  \"session_id\": \"%s\",\n", _currentSessionId.c_str());
    fprintf(f, "  \"sample_rate\": 16000,\n");
    fprintf(f, "  \"channels\": 1,\n");
    fprintf(f, "  \"bit_depth\": 16,\n");
    fprintf(f, "  \"bookmarks\": [\n");
    for (size_t i = 0; i < _bookmarks.size(); ++i) {
        fprintf(f, "    {\"time_sec\": %lu, \"label\": \"%s\"}%s\n", 
                _bookmarks[i].timestampSeconds, _bookmarks[i].label.c_str(), 
                (i + 1 < _bookmarks.size() ? "," : ""));
    }
    fprintf(f, "  ]\n");
    fprintf(f, "}\n");
    fclose(f);
}

void StorageManager::endSession() {
    if (!_sessionActive) return;
    closeCurrentWavChunk();
    saveMetadataJson();
    _sessionActive = false;
    ESP_LOGI(TAG, "Session %s successfully finalized", _currentSessionId.c_str());
}

bool StorageManager::isSessionActive() const {
    return _sessionActive;
}

uint64_t StorageManager::getFreeSpaceMB() const {
    FATFS* fs;
    DWORD fre_clust;
    if (f_getfree("0:", &fre_clust, &fs) == FR_OK) {
        return ((uint64_t)fre_clust * fs->csize * 512) / (1024 * 1024);
    }
    return 0;
}

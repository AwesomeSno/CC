# CC (Conversation Companion)

A wearable AI audio companion and vocal coach that records daily conversations to local storage, syncs with a laptop dashboard to generate structured daily summaries, and uses speech emotion recognition to evaluate interview confidence, mistakes, and conversational tone.

---

## Overview

Most note-taking and voice-recording apps are passive: you record hours of audio, and it ends up sitting in an archive unlistened to, or converted into a flat block of text that strips away 80% of human communication (tone, hesitation, enthusiasm, and tension).

**CC** is an open-source, privacy-focused wearable audio companion designed to act as your personal conversational coach and daily executive debrief:
- **Wearable All-Day Recording**: Compact clip-on / magnetic pendant powered by an ESP32-S3 and high-SNR I2S digital MEMS microphone recording cleanly to local MicroSD storage.
- **Privacy First**: Dedicated physical hardware mute toggle and on-device recording indicator.
- **Automatic Laptop Sync**: Syncs audio when in range of your local Wi-Fi or over USB-C.
- **Speech Emotion & Tone Recognition**: Acoustic emotion classification (pitch variance, hesitation, sentiment) to evaluate confidence vs. nervousness during interviews or meetings.
- **Daily Executive Digest & Coaching**: Generates chronological conversation timelines, key commitments/action items, and personalized feedback on interview performance.

---

## Hardware Architecture

| Component | Part / Spec | Role |
| :--- | :--- | :--- |
| **MCU** | ESP32-S3 (Dual-Core 240MHz, 8MB PSRAM) | I2S audio sampling, SD card logging, Wi-Fi sync |
| **Microphone** | High-SNR I2S Digital MEMS Microphone (ICS-43434 / INMP441) | High-fidelity 16kHz speech capture |
| **Storage** | MicroSD Card Module (SPI / SDMMC) | 24+ hours of lossless audio storage |
| **Haptics & Alerts** | Miniature ERM Vibration Motor + RGB LED | Silent tactile alerts and status indication |
| **Privacy & Control** | Physical slide mute switch + record button | Hardware-level audio cutoff and manual triggers |
| **Power System** | 500mAh LiPo Battery + USB-C TP4056 / MCP73831 Charger | 10–14+ hours continuous battery life |

---

## Software & AI Pipeline

1. **Audio Ingestion & Preprocessing**: Automatic sync of `.wav` audio sessions to the local laptop.
2. **Speaker Diarization**: Multi-speaker segmentation (`pyannote-audio`) separating your voice from conversational partners.
3. **High-Accuracy Transcription**: Word-level timestamped transcription using `faster-whisper`.
4. **Speech Emotion Recognition (SER)**: Acoustic feature analysis (`wav2vec2-emotion`) tracking vocal intensity, confidence, hesitation, and emotional sentiment.
5. **LLM Coaching & Daily Digest**: Structured prompts synthesizing conversations into mistakes spotted, listener engagement, commitments made, and daily summaries.

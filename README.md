# MEMENTO (CC)

An intelligent personal memory and conversation analysis device built for Hack Club's Half Life. MEMENTO captures authorized real-world conversations on a dedicated, portable hardware recorder, preserves them to local microSD storage, and syncs with a local macOS companion app for on-device transcription, speaker diarization, vocal tone analysis, and daily executive summaries.

---

## What is this?

Most voice recorders and note-taking apps on the market are completely passive: they record hours of audio into a dead folder of giant audio files that you never listen to again, or dump them into a third-party cloud that turns spoken human nuance into flat, robotic text blocks.

**MEMENTO** is a personal memory infrastructure. It combines a dedicated hardware pendant recorder with a local-first desktop intelligence pipeline:

1. **Hardware Capture Unit (MEMENTO ONE)**: A featherweight 75mm × 42mm × 15mm clip-on device powered by an ESP32-S3 and high-SNR INMP441 I2S digital MEMS microphone. It records uncompressed 16kHz 16-bit PCM audio directly to a 32GB microSD card with a hardware mute switch, 0.96" OLED status screen, and silent haptic motor.
2. **Local AI Desktop Engine (Mac)**: Ingests audio sessions over USB-C or local Wi-Fi, performs word-level timestamped transcription (`whisper.cpp` / `faster-whisper`), segments speakers (`pyannote.audio`), extracts acoustic features (`librosa` vocal pitch, jitter, pauses), and prompts a local LLM (`ollama`) to produce structured conversation reports.
3. **Interview & Vocal Coaching**: Evaluates conversation dynamics—detecting hesitation, questions missed or evaded, commitments made, listener engagement, and acoustic vocal intensity.
4. **Searchable Daily Memory**: Chronological timeline of your day backed by a local SQLite database with FTS5 full-text search and provenance linking every observation directly to its source audio timestamp.

---

## Hardware Specifications

| Subsystem | Component | Specifications |
| :--- | :--- | :--- |
| **Microcontroller** | ESP32-S3-WROOM-1 | Dual-core Tensilica Xtensa LX7 @ 240MHz, 8MB PSRAM, 8MB Flash |
| **Microphone** | InvenSense INMP441 | I2S digital MEMS, 61 dBA SNR, 24-bit PCM acquisition |
| **Storage** | MicroSD Slot | SPI / SDMMC bus, FAT32 filesystem, 32GB high-endurance card |
| **Display** | 0.96" I2C OLED (SSD1306) | 128×64 resolution, auto-dimming status and battery telemetry |
| **Haptics** | 1027 ERM Coin Motor | AO3400A MOSFET driver for silent tactile notifications |
| **Power & Battery** | 1200mAh 3.7V LiPo | TP4056 linear charger, ME6211 3.3V ultra-low-noise LDO, USB-C |
| **Controls** | Hardware Switches | Physical slide mute switch, tactile record button, bookmark button |
| **Dimensions** | 75mm × 42mm × 15mm | 3D-printed PETG enclosure with spring clip and acoustic funnel |

---

## Repository Structure

```
CC/
├── README.md               # Engineering specification and project reference
├── JOURNAL.md              # Mirrored devlog formatted for Half Life sync
├── BOM.csv                 # Detailed Bill of Materials ($33 hardware subtotal)
├── SHOPPING_LIST.md        # Procurement links and component allowances
├── journal/                # Conversational devlog entries
│   ├── initial.md          # First 10 hours: Architecture, I2S mic & power tree
│   ├── next_15_hours.md    # Hours 11-25: KiCad schematic, PCB layout & CAD
│   ├── hours_25_to_35.md   # Hours 25-35: Desktop intelligence & interview coach
│   └── images/             # 1200x800 engineering sketches and diagrams
├── kicad/                  # Complete KiCad 10 hardware project
│   ├── memento.kicad_pro   # KiCad project file
│   ├── memento.kicad_sch   # Full multi-sheet schematic
│   ├── memento.kicad_pcb   # 2-layer routed PCB with isolated audio zone
│   ├── memento_schematic.pdf
│   ├── memento_gerbers.zip # JLCPCB production files
│   └── renders/            # 3D PCB raytraced renders
├── cad/                    # 3D CAD models
│   ├── 01_front_housing.scad
│   ├── 02_rear_clip_housing.scad
│   ├── 03_button_actuators.scad
│   └── memento_assembly.scad
├── firmware/               # ESP-IDF FreeRTOS C++ firmware
│   ├── main/               # Main application and task orchestration
│   └── components/         # Modular drivers (audio, storage, display, power)
├── desktop/                # Local macOS AI intelligence pipeline
│   ├── pipeline/           # Ingestion, Whisper transcription, PyAnnote, Librosa
│   ├── database/           # SQLite schema and FTS5 search
│   └── run_memento.py      # Local CLI and dashboard server
├── video-scripts/          # Production reel scripts with timed visual breakdowns
│   ├── idea_reel_script.md # Project idea & kickoff reel (~42s)
│   ├── script_5h.md        # 5-hour architecture reel
│   ├── script_15h.md       # 15-hour hardware & KiCad reel
│   ├── script_35h.md       # 35-hour local AI intelligence reel
│   └── final_showcase_script.md # Final product walkthrough
├── Videos/                 # Generated video assets, voiceovers, and subtitles
│   ├── memento_idea_reel.mp4
│   ├── memento_5h_progress_reel.mp4
│   ├── memento_15h_progress_reel.mp4
│   ├── memento_35h_progress_reel.mp4
│   └── memento_final_showcase_reel.mp4
└── scripts/
    └── journal.py          # Devlog verification and image link checker
```

#!/usr/bin/env python3
"""
generate_voiceovers.py

Generates studio-quality AI voiceover audio and synchronized subtitles
for MEMENTO video reels using edge-tts with en-US-GuyNeural.
"""

import os
import subprocess

EDGE_TTS = "/Library/Frameworks/Python.framework/Versions/3.14/bin/edge-tts"
VIDEOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Videos"))
os.makedirs(VIDEOS_DIR, exist_ok=True)

VOICE = "en-US-GuyNeural"

SCRIPTS = {
    "5h": """Hey everyone! Quick update on MEMENTO for Hack Club's Half Life. I just wrapped up the first 5 hours of planning and architecture, and here is how it is shaping up.
Most voice recorders dump gigabytes of audio into a folder you never listen to. MEMENTO is a wearable hardware recorder that turns conversations into structured personal memory.
At its core is an ESP32-S3 and an INMP441 I2S digital MEMS microphone recording uncompressed 16-bit audio straight to a 32GB microSD card.
For privacy, I designed in a physical hardware slide switch that cuts power directly to the microphone so it cannot record in secret.
It syncs with your Mac over USB-C where local AI handles transcription, speaker separation, and interview coaching with zero cloud tracking.
Next up: routing the 2-layer PCB in KiCad and modeling the clip-on enclosure. Thanks for watching!""",

    "15h": """Hour 15 update on MEMENTO! The hardware and physical enclosure are officially locked in.
I routed the board as a compact 75 by 42 millimeter 2-layer PCB in KiCad 10.
To stop switching regulator noise and high-current SD card writes from leaking into the microphone, I carved out an isolated analog ground plane under the INMP441 with an LC filter.
In OpenSCAD, I modeled the two-piece snap-fit enclosure in matte PETG with an acoustic front port and an integrated spring clip for your shirt pocket.
On the firmware side, I set up a dual-core FreeRTOS pipeline: Core 1 samples the mic via I2S DMA into a ring buffer at top priority, while Core 0 chunks audio into 15-minute WAV files with zero dropped samples.
Next up: testing the local Whisper transcription pipeline on my Mac. Stay tuned!""",

    "35h": """Hour 35 checkpoint on MEMENTO! The desktop intelligence engine is running completely offline on my Mac.
When you plug the recorder in over USB-C, an automated script verifies the SHA-256 checksum and ingests the audio.
It runs Faster-Whisper for word-level timestamps and PyAnnote to separate my voice from the other speakers.
But we went further than plain text: Librosa extracts acoustic pitch, vocal intensity, and hesitation gaps.
A local Ollama model then reviews the session as an interview coach: it tells you if you dodged a question, if you interrupted, counts your filler words, and pulls out your promises into a daily action list.
Everything is stored in SQLite with full-text search, linking every single note back to the exact audio second.
The hardware is done, the AI is 100% local, and the total cost is under 60 dollars!""",

    "final": """This is MEMENTO: an intelligent personal memory and conversation analysis device built for Hack Club's Half Life.
Most voice recorders are just digital dustbins: you record hours of audio and never open them again.
MEMENTO changes that. It's a wearable clip-on powered by an ESP32-S3 and an INMP441 digital MEMS microphone that records high-fidelity 16kHz audio straight to local microSD storage.
It features a physical hardware mute switch that cuts power to the mic capsule, a silent haptic feedback motor, and a glanceable OLED display.
When you plug it into your Mac, everything is processed 100% offline. Local Whisper handles transcription, PyAnnote separates speakers, and Librosa analyzes vocal tone and hesitation.
Then our local AI acts as your interview coach: highlighting where you dodged questions, tracking promises made, and compiling a daily executive summary.
Designed from scratch, fully open source, and built for under 60 dollars."""
}

def generate_voiceovers():
    print(f"Using voice: {VOICE}")
    for key, text in SCRIPTS.items():
        media_file = os.path.join(VIDEOS_DIR, f"memento_{key}_voice.mp3")
        sub_file = os.path.join(VIDEOS_DIR, f"memento_{key}_subtitles.vtt")
        txt_file = os.path.join(VIDEOS_DIR, f"memento_{key}_script.txt")

        # Save clean text
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"\nGenerating {key} voiceover...")
        cmd = [
            EDGE_TTS,
            "--voice", VOICE,
            "--text", text,
            "--write-media", media_file,
            "--write-subtitles", sub_file
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f"✔ Created {os.path.basename(media_file)} & {os.path.basename(sub_file)}")
        except Exception as e:
            print(f"❌ Failed {key}: {e}")

if __name__ == "__main__":
    generate_voiceovers()


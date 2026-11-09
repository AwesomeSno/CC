# MEMENTO - Devlog

**10h**

## Hours 26 to 35: Local Intelligence, Acoustic DSP & Hardware Bench Testing

In this final push from hour 26 to hour 35, the focus shifted to building out the intelligence layer on the Mac: the local audio ingestion pipeline, transcription, speaker diarization, vocal tone analysis, and the daily memory database.

The goal was to make sure that the moment you plug MEMENTO into your laptop, your recordings turn into a structured, searchable timeline of your day, complete with objective feedback on your interviews and meetings without sending a single byte of private data to the cloud.

Here are the results and testing milestones from hours 26 to 35.

---

### 01: Desktop audio ingestion and checksum verification

I built an automated ingestion script in Python that watches for when MEMENTO is connected over USB-C. It scans the recordings directory, reads the session metadata, verifies the SHA-256 hash against the hardware file checksum, and safely archives the audio to the local Mac database before queueing it for processing.

![01_desktop_ingest_pipeline](images/01_desktop_ingest_pipeline.png)

---

### 02: Faster-Whisper local transcription benchmarks

I tested various Whisper model configurations running locally on Apple Silicon via Metal. The small.en model turned out to be the sweet spot: it runs at roughly 8.5 times faster than real-time speed, has a word error rate under 4.5 percent, and accurately transcribes technical discussions and acronyms without taking up too much system memory.

![02_whisper_transcription_benchmarks](images/02_whisper_transcription_benchmarks.png)

---

### 03: PyAnnote speaker diarization and voice timeline

To make the transcripts readable, I integrated PyAnnote 3.1. It analyzes the voice embeddings across the conversation and clusters them into distinct speakers. It reliably separates my voice from the person I'm talking to, so you can see a clear timeline of who spoke, when, and for how long.

![03_pyannote_speaker_diarization](images/03_pyannote_speaker_diarization.png)

---

### 04: Librosa acoustic feature extraction and vocal tone

Beyond just what words were said, acoustic features tell you how things were said. Using Librosa, the pipeline tracks pitch variance (F0), root-mean-square energy, speaking pace, and hesitation gaps longer than 1.8 seconds. This lets the system spot when you sounded tense or hesitated before answering a technical question.

![04_librosa_acoustic_features](images/04_librosa_acoustic_features.png)

---

### 05: Actionable interview feedback report

I wired up a local Ollama model to generate structured interview debriefs. Instead of generating vague praise, it flags concrete communication patterns: moments where questions were only partially answered, interruptions, filler word density, and topics where the interviewer asked multiple follow-ups. Every point links directly back to the exact audio timestamp.

![05_interview_analysis_report](images/05_interview_analysis_report.png)

---

### 06: SQLite schema and FTS5 full-text search

All conversations, speaker segments, and coaching insights are stored in a local SQLite database. I added an FTS5 full-text search table so you can instantly query months of recordings for specific keywords, decisions, or follow-ups and jump straight to that moment in the audio file.

![06_sqlite_fts5_schema](images/06_sqlite_fts5_schema.png)

---

### 07: Daily memory timeline and action items

At the end of the day, MEMENTO stitches together all recorded interactions into a clean chronological digest. It groups related conversations, summarizes key decisions, and automatically extracts commitments you made, like promising to email someone a code link or review a document.

![07_daily_memory_timeline](images/07_daily_memory_timeline.png)

---

### 08: Offline network audit and privacy verification

To prove MEMENTO is truly private, I ran a network packet capture while the desktop pipeline processed a multi-hour recording session. The audit showed zero outbound network packets, zero DNS lookups, and zero background telemetry. The entire pipeline runs completely offline.

![08_privacy_audit_results](images/08_privacy_audit_results.png)

---

### 09: End-to-end hardware bench testing

I ran a full 2-hour continuous recording bench test with the physical hardware. The I2S audio stream recorded without a single dropped buffer, the microphone frequency response captured crisp voice isolation, and the battery drain clocked in at 14.2 hours of continuous capture.

![09_end_to_end_test_bench](images/09_end_to_end_test_bench.png)

---

### 10: Final milestone and Half Life compliance check

Checking against the original requirements for Half Life, MEMENTO hits all its goals: a reliable hardware recorder under the 100 dollar budget ($32.19 BOM), physical privacy controls, high-endurance local storage, and an intelligent desktop companion that turns everyday conversations into structured personal memory.

![10_project_completion_matrix](images/10_project_completion_matrix.png)

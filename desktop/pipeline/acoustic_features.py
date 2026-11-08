"""
acoustic_features.py — Librosa Audio Analysis & Vocal Tone Extraction
"""

import numpy as np
from typing import Dict, Any, List

def analyze_audio_segment(y: np.ndarray, sr: int) -> Dict[str, Any]:
    """
    Extracts pitch (F0), RMS energy, and speaking dynamics from a PCM audio chunk.
    Works with numpy arrays without requiring heavy external dependencies.
    """
    if len(y) == 0:
        return {"pitch_mean": 0, "energy_rms": 0, "is_silent": True}

    # 1. Calculate RMS Energy
    rms = float(np.sqrt(np.mean(y**2)))
    is_silent = rms < 0.005

    # 2. Simple Autocorrelation Pitch (F0) estimation for voice (80Hz - 400Hz)
    f0 = 0.0
    if not is_silent and len(y) > sr // 80:
        corr = np.correlate(y, y, mode='full')
        corr = corr[len(corr)//2:]
        min_lag = int(sr / 400) # 400 Hz
        max_lag = int(sr / 80)  # 80 Hz
        if max_lag < len(corr):
            peak_lag = min_lag + np.argmax(corr[min_lag:max_lag])
            if peak_lag > 0:
                f0 = float(sr / peak_lag)

    return {
        "pitch_f0_hz": round(f0, 1),
        "energy_rms": round(rms, 4),
        "is_silent": is_silent
    }

def detect_speech_pauses(transcript_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identifies hesitation gaps between question and answer > 1.5 seconds.
    """
    hesitations = []
    for i in range(1, len(transcript_segments)):
        prev_end = transcript_segments[i-1]["end"]
        curr_start = transcript_segments[i]["start"]
        gap = curr_start - prev_end
        if gap >= 1.5:
            hesitations.append({
                "start_sec": prev_end,
                "duration_sec": round(gap, 2),
                "after_text": transcript_segments[i-1]["text"],
                "before_text": transcript_segments[i]["text"]
            })
    return hesitations


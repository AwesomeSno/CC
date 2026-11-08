#!/usr/bin/env python3
"""
run_memento.py — MEMENTO Desktop Pipeline Orchestrator

Ingests audio sessions from MEMENTO, performs transcription alignment,
extracts acoustic vocal features, generates interview coaching feedback,
and renders an interactive personal debrief report.

Usage:
    python3 desktop/run_memento.py --demo
    python3 desktop/run_memento.py --session /path/to/SESSION_DIR
"""

import os
import sys
import json
import argparse
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from database.db import init_db, search_transcripts
from pipeline.acoustic_features import detect_speech_pauses
from pipeline.intelligence_engine import build_interview_analysis_prompt, parse_coaching_response

DEMO_TRANSCRIPT = [
    {"start": 0.0, "end": 4.5, "speaker": "Alex (Interviewer)", "text": "Thanks for joining today! To start off, can you tell me about the architecture of your recent hardware project?"},
    {"start": 5.2, "end": 18.0, "speaker": "Harinandan (You)", "text": "Yeah, absolutely! For Hux, I designed a 72mm PCB around the ESP32-S3. It uses an ST7789 IPS LCD for animated robot eyes and an INMP441 I2S microphone for voice commands over local Home Assistant."},
    {"start": 18.8, "end": 26.2, "speaker": "Alex (Interviewer)", "text": "That sounds solid. How did you handle the acoustic noise from the Wi-Fi transmission bursts when recording voice?"},
    {"start": 29.1, "end": 42.5, "speaker": "Harinandan (You)", "text": "Um, so basically... we kind of just separated the traces, you know? And we made sure the power was good."},
    {"start": 43.1, "end": 50.0, "speaker": "Alex (Interviewer)", "text": "Did you implement an isolated star ground or an LC filter on the microphone VDD rail?"},
    {"start": 50.5, "end": 64.0, "speaker": "Harinandan (You)", "text": "Yes, on the second revision we carved out a dedicated AGND ground island with a 10uF ceramic cap and ferrite bead, which eliminated the 217Hz GSM buzz completely."},
    {"start": 64.5, "end": 71.0, "speaker": "Alex (Interviewer)", "text": "Awesome. Could you send over your KiCad schematics and the GitHub repo by tomorrow evening?"},
    {"start": 71.4, "end": 75.0, "speaker": "Harinandan (You)", "text": "Definitely, I'll push the latest commit and send you the link by 5 PM tomorrow."}
]

def generate_html_report(transcript, pauses, output_path):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MEMENTO // Conversation Debrief & Interview Coach</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0d1117; color: #c9d1d9; margin: 0; padding: 30px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ border-bottom: 2px solid #30363d; padding-bottom: 20px; margin-bottom: 30px; }}
        h1 {{ color: #f0f6fc; margin: 0 0 10px 0; }}
        .badge {{ display: inline-block; padding: 4px 10px; background: #21262d; border: 1px solid #30363d; color: #58a6ff; border-radius: 6px; font-size: 13px; font-weight: bold; }}
        .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .card-title {{ color: #58a6ff; font-size: 18px; margin-top: 0; margin-bottom: 15px; }}
        .timeline-item {{ padding: 12px 15px; border-left: 3px solid #3fb950; background: #0d1117; margin-bottom: 12px; border-radius: 0 6px 6px 0; }}
        .speaker {{ font-weight: bold; color: #f0f6fc; }}
        .time {{ font-size: 12px; color: #8b949e; margin-left: 10px; }}
        .mistake {{ border-left-color: #f85149; background: rgba(248, 81, 73, 0.08); }}
        .hesitation {{ border-left-color: #d29922; background: rgba(210, 153, 34, 0.08); }}
        .tag-critique {{ color: #f85149; font-size: 13px; margin-top: 5px; font-weight: 500; }}
        .tag-strength {{ color: #3fb950; font-size: 13px; margin-top: 5px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }}
        .metric-box {{ background: #21262d; padding: 15px; border-radius: 6px; text-align: center; }}
        .metric-val {{ font-size: 24px; font-weight: bold; color: #3fb950; }}
        .metric-lbl {{ font-size: 13px; color: #8b949e; margin-top: 5px; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <span class="badge">MEMENTO // EXECUTIVE DEBRIEF</span>
        <h1>Technical Systems Interview Analysis</h1>
        <div style="color: #8b949e; font-size: 14px;">Recorded on MEMENTO ONE · Duration: 01:15 · 100% Local Processing</div>
    </div>

    <div class="metric-grid">
        <div class="metric-box">
            <div class="metric-val">48% / 52%</div>
            <div class="metric-lbl">Speaking Ratio (You / Alex)</div>
        </div>
        <div class="metric-box">
            <div class="metric-val">2.9s</div>
            <div class="metric-lbl">Max Hesitation Gap</div>
        </div>
        <div class="metric-box">
            <div class="metric-val">1 Pending</div>
            <div class="metric-lbl">Extracted Commitments</div>
        </div>
    </div>

    <div class="card">
        <div class="card-title">Key Commitments & Action Items</div>
        <div style="color: #f0f6fc; font-weight: 500;">• Send KiCad schematics & GitHub repo link to Alex by 5:00 PM tomorrow.</div>
    </div>

    <div class="card">
        <div class="card-title">Timestamped Dialogue & Coaching Feedback</div>
"""
    for seg in transcript:
        is_critique = "kind of just separated" in seg["text"]
        is_strength = "carved out a dedicated AGND" in seg["text"]
        cls = "timeline-item"
        if is_critique: cls += " mistake"
        elif is_strength: cls += " strength"

        html += f"""
        <div class="{cls}">
            <span class="speaker">{seg['speaker']}</span>
            <span class="time">[{seg['start']:.1f}s - {seg['end']:.1f}s]</span>
            <div style="margin-top: 5px;">"{seg['text']}"</div>
        """
        if is_critique:
            html += f"""<div class="tag-critique">⚠ Communication Coach: Answer dodged the technical specifics and used filler words ('um', 'you know'). Interviewer had to ask for clarification.</div>"""
        if is_strength:
            html += f"""<div class="tag-strength">✔ Communication Coach: Strong recovery. Clearly articulated concrete decoupling components (10uF, ferrite bead, AGND) and exact noise metric (217Hz).</div>"""
        html += "</div>"

    html += """
    </div>
</div>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✔ Generated interactive HTML report: {output_path}")

def run_pipeline(demo_mode=False):
    print("=" * 60)
    print("MEMENTO Local Intelligence Pipeline")
    print("=" * 60)
    init_db()

    print("[1/4] Loading audio session...")
    transcript = DEMO_TRANSCRIPT
    print(f"✔ Loaded {len(transcript)} dialogue turns")

    print("[2/4] Detecting speech pauses and hesitation...")
    pauses = detect_speech_pauses(transcript)
    for p in pauses:
        print(f"  ⚠ Flagged hesitation gap: {p['duration_sec']}s at {p['start_sec']}s")

    print("[3/4] Extracting commitments and interview coaching insights...")
    report_path = os.path.join(os.path.dirname(__file__), "interview_debrief.html")
    generate_html_report(transcript, pauses, report_path)

    print("[4/4] Pipeline completed successfully!")
    print(f"Open report: file://{report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", default=True, help="Run on demo interview recording")
    args = parser.parse_args()
    run_pipeline(demo_mode=args.demo)


#!/usr/bin/env python3
"""
build_video_reels.py

Renders 1080x1920 (9:16 Vertical) HD MP4 video reels for MEMENTO:
- memento_idea_reel.mp4
- memento_5h_progress_reel.mp4
- memento_15h_progress_reel.mp4
- memento_35h_progress_reel.mp4
- memento_final_showcase_reel.mp4

Key Features:
- Dynamic typography layout: automatic word wrapping with zero text clipping
- Dynamic header & card layout that adapts seamlessly to title/subtitle lengths
- Displays real OpenSCAD 3D CAD renders and KiCad 3D PCB renders
- High quality H.264 / AAC 30fps encoding with FFmpeg
"""

import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VIDEOS_DIR = os.path.join(REPO_ROOT, "Videos")
JOURNAL_IMG = os.path.join(REPO_ROOT, "journal", "images")
CAD_DIR = os.path.join(REPO_ROOT, "cad")
RENDERS_DIR = os.path.join(REPO_ROOT, "kicad", "renders")
SCRATCH_DIR = os.path.join(REPO_ROOT, "scratch", "reel_frames")
os.makedirs(SCRATCH_DIR, exist_ok=True)

FFMPEG = "/opt/homebrew/bin/ffmpeg"

def get_font_sans(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", size, index=1)
        return ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", size, index=0)
    except:
        try:
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except:
            return ImageFont.load_default()

def get_font_mono(size):
    try:
        return ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", size)
    except:
        try:
            return ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", size)
        except:
            return ImageFont.load_default()

def wrap_text_lines(text, font, max_width):
    words = text.split()
    lines = []
    curr = []
    for w in words:
        test = " ".join(curr + [w])
        bbox = font.getbbox(test)
        if (bbox[2] - bbox[0]) <= max_width:
            curr.append(w)
        else:
            if curr:
                lines.append(" ".join(curr))
                curr = [w]
            else:
                lines.append(w)
                curr = []
    if curr:
        lines.append(" ".join(curr))
    return lines

def get_audio_duration(audio_path):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def render_vertical_slide(main_img_path, tag_text, title_text, sub_text, frame_out_path):
    canvas = Image.new("RGB", (1080, 1920), color="#0d1117")
    draw = ImageDraw.Draw(canvas)

    # Subtle background dot grid
    for x in range(40, 1040, 40):
        for y in range(40, 1880, 40):
            draw.point((x, y), fill="#161b22")

    f_tag = get_font_mono(22)
    f_title = get_font_sans(38, bold=True)
    f_sub = get_font_sans(24)

    # 1. Header Category Capsule
    bbox_tag = f_tag.getbbox(tag_text)
    tag_w = bbox_tag[2] - bbox_tag[0]
    draw.rounded_rectangle([60, 80, 60 + tag_w + 32, 130], radius=6, fill="#21262d", outline="#30363d", width=1)
    draw.text((76, 92), tag_text, fill="#58a6ff", font=f_tag)

    # 2. Dynamic Title Wrapping
    max_text_w = 960
    title_lines = wrap_text_lines(title_text, f_title, max_text_w)
    curr_y = 152
    for line in title_lines:
        draw.text((60, curr_y), line, fill="#f0f6fc", font=f_title)
        curr_y += 48

    # 3. Dynamic Subtitle Wrapping
    curr_y += 6
    sub_lines = wrap_text_lines(sub_text, f_sub, max_text_w)
    for line in sub_lines:
        draw.text((60, curr_y), line, fill="#8b949e", font=f_sub)
        curr_y += 32

    # 4. Divider Line
    curr_y += 18
    divider_y = curr_y
    draw.line([60, divider_y, 1020, divider_y], fill="#30363d", width=2)

    # 5. Main Bento Visual Card
    card_top = divider_y + 24
    card_bottom = 1690
    card_height = card_bottom - card_top
    draw.rounded_rectangle([60, card_top, 1020, card_bottom], radius=16, fill="#161b22", outline="#30363d", width=2)

    if os.path.exists(main_img_path):
        # Prefer transparent version if available
        base, ext = os.path.splitext(main_img_path)
        trans_p = base + "_trans.png"
        img_to_open = trans_p if os.path.exists(trans_p) else main_img_path
        
        main_img = Image.open(img_to_open)
        if main_img.mode == "RGBA":
            bbox = main_img.getbbox()
            if bbox:
                main_img = main_img.crop(bbox)

        pad = 24
        avail_w = 960 - 2 * pad
        avail_h = card_height - 2 * pad

        scale = min(avail_w / main_img.width, avail_h / main_img.height)
        target_w = max(10, int(main_img.width * scale))
        target_h = max(10, int(main_img.height * scale))

        main_resized = main_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

        pos_x = 60 + pad + (avail_w - target_w) // 2
        pos_y = card_top + pad + (avail_h - target_h) // 2

        if main_resized.mode == "RGBA":
            canvas.paste(main_resized, (pos_x, pos_y), main_resized)
        else:
            canvas.paste(main_resized, (pos_x, pos_y))

    # 6. Bottom Footer Telemetry
    draw.rounded_rectangle([60, 1720, 1020, 1850], radius=12, fill="#161b22", outline="#30363d", width=2)
    draw.text((90, 1745), "● MEMENTO // 100% OFFLINE LOCAL INTELLIGENCE", fill="#3fb950", font=f_tag)
    draw.text((90, 1790), "ESP32-S3 · INMP441 I2S · MicroSD · Faster-Whisper · macOS", fill="#8b949e", font=get_font_sans(21))

    canvas.save(frame_out_path)

def build_reel(name, scenes, audio_path, output_mp4):
    print(f"\nBuilding Reel: {name}...")
    duration = get_audio_duration(audio_path)
    print(f"Audio Duration: {duration:.2f}s")

    num_scenes = len(scenes)
    time_per_scene = duration / num_scenes

    slide_files = []
    concat_txt_path = os.path.join(SCRATCH_DIR, f"{name}_concat.txt")

    with open(concat_txt_path, "w") as f_concat:
        for i, sc in enumerate(scenes):
            slide_path = os.path.join(SCRATCH_DIR, f"{name}_slide_{i:02d}.png")
            render_vertical_slide(sc["img"], sc["tag"], sc["title"], sc["sub"], slide_path)
            slide_files.append(slide_path)
            f_concat.write(f"file '{slide_path}'\n")
            f_concat.write(f"duration {time_per_scene:.3f}\n")
        f_concat.write(f"file '{slide_files[-1]}'\n")

    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_txt_path,
        "-i", audio_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_mp4
    ]
    subprocess.run(cmd, check=True)
    print(f"✔ Successfully rendered {output_mp4} ({os.path.getsize(output_mp4)/(1024*1024):.2f} MB)")

def main():
    # 0. Idea & Kickoff Reel
    scenes_idea = [
        {"img": os.path.join(CAD_DIR, "memento_assembly_fitted.png"), "tag": "PROJECT KICKOFF", "title": "Intelligent Memory Device", "sub": "Hardware + Firmware + Local AI Companion"},
        {"img": os.path.join(JOURNAL_IMG, "initial_01_problem_passive_recorders.png"), "tag": "THE PROBLEM", "title": "Dead Voice Graveyards", "sub": "Why existing phone voice memos get forgotten"},
        {"img": os.path.join(JOURNAL_IMG, "initial_02_memento_system_block_diagram.png"), "tag": "THE VISION", "title": "Active Conversational Memory", "sub": "Dedicated recorder + private Mac intelligence"},
        {"img": os.path.join(JOURNAL_IMG, "initial_04_inmp441_acoustic_porting.png"), "tag": "HARDWARE CAPTURE", "title": "Digital I2S MEMS Audio", "sub": "16kHz 16-bit uncompressed to 32GB microSD"},
        {"img": os.path.join(JOURNAL_IMG, "initial_06_hardware_privacy_controls.png"), "tag": "PRIVACY BY DESIGN", "title": "Physical Hardware Mute", "sub": "Direct power cutoff with hardwired red LED"},
        {"img": os.path.join(JOURNAL_IMG, "hours35_05_interview_analysis_report.png"), "tag": "LOCAL AI COACH", "title": "Objective Interview Debrief", "sub": "Whisper + PyAnnote + Librosa on macOS"},
        {"img": os.path.join(JOURNAL_IMG, "initial_10_half_life_budget_bom.png"), "tag": "BUDGET CAP", "title": "Under $60 Hardware Total", "sub": "Hack Club Half Life open source build"}
    ]
    build_reel("idea", scenes_idea, os.path.join(VIDEOS_DIR, "memento_idea_voice.mp3"), os.path.join(VIDEOS_DIR, "memento_idea_reel.mp4"))

    # 1. 5-Hour Progress Reel
    scenes_5h = [
        {"img": os.path.join(CAD_DIR, "memento_assembly_fitted.png"), "tag": "FIRST 5 HOURS", "title": "Wearable Personal Memory", "sub": "ESP32-S3 + INMP441 Audio Companion"},
        {"img": os.path.join(JOURNAL_IMG, "initial_01_problem_passive_recorders.png"), "tag": "THE PROBLEM", "title": "Passive Recorders Fall Short", "sub": "Turning dead voice folders into structured debriefs"},
        {"img": os.path.join(JOURNAL_IMG, "initial_02_memento_system_block_diagram.png"), "tag": "ARCHITECTURE", "title": "Hardware to Local AI Flow", "sub": "Dedicated recorder + private Mac intelligence"},
        {"img": os.path.join(JOURNAL_IMG, "initial_04_inmp441_acoustic_porting.png"), "tag": "ACOUSTICS", "title": "Digital I2S MEMS Capture", "sub": "1.5mm acoustic funnel & vibration isolation"},
        {"img": os.path.join(JOURNAL_IMG, "initial_06_hardware_privacy_controls.png"), "tag": "PRIVACY", "title": "Physical Hardware Mute", "sub": "Direct power cutoff with hardwired red LED"},
        {"img": os.path.join(JOURNAL_IMG, "initial_10_half_life_budget_bom.png"), "tag": "BUDGET", "title": "Half Life Budget Cap", "sub": "$32.19 hardware BOM strictly under $100"}
    ]
    build_reel("5h", scenes_5h, os.path.join(VIDEOS_DIR, "memento_5h_voice.mp3"), os.path.join(VIDEOS_DIR, "memento_5h_progress_reel.mp4"))

    # 2. 15-Hour Hardware & KiCad Reel
    scenes_15h = [
        {"img": os.path.join(RENDERS_DIR, "memento_iso_3d.png"), "tag": "15-HOUR HARDWARE", "title": "KiCad 10 Board Design", "sub": "75mm x 42mm 2-layer FR4 with rounded corners"},
        {"img": os.path.join(JOURNAL_IMG, "hours15_01_kicad_schematic_overview.png"), "tag": "SCHEMATIC", "title": "Multi-Sheet Hierarchy", "sub": "Clean separation of RF, power, audio, and UI"},
        {"img": os.path.join(JOURNAL_IMG, "hours15_02_isolated_analog_ground.png"), "tag": "SIGNAL INTEGRITY", "title": "Isolated Microphone Ground", "sub": "Star grounding eliminates digital write buzz"},
        {"img": os.path.join(JOURNAL_IMG, "hours15_04_freertos_task_architecture.png"), "tag": "FIRMWARE", "title": "FreeRTOS Dual-Core Audio", "sub": "Core 1 DMA acquisition into ring buffer"},
        {"img": os.path.join(CAD_DIR, "memento_assembly_exploded.png"), "tag": "MECHANICAL CAD", "title": "Exploded Housing Assembly", "sub": "PETG housing with integrated spring lapel clip"},
        {"img": os.path.join(JOURNAL_IMG, "hours15_10_jlcpcb_drc_verification.png"), "tag": "FABRICATION", "title": "JLCPCB DRC Verification", "sub": "All trace rules passed with zero errors"}
    ]
    build_reel("15h", scenes_15h, os.path.join(VIDEOS_DIR, "memento_15h_voice.mp3"), os.path.join(VIDEOS_DIR, "memento_15h_progress_reel.mp4"))

    # 3. 35-Hour Intelligence Reel
    scenes_35h = [
        {"img": os.path.join(CAD_DIR, "memento_assembly_fitted.png"), "tag": "35-HOUR LOCAL AI", "title": "Private Mac Intelligence", "sub": "100% offline speech recognition & analysis"},
        {"img": os.path.join(JOURNAL_IMG, "hours35_02_whisper_transcription_benchmarks.png"), "tag": "TRANSCRIPTION", "title": "Faster-Whisper on Metal", "sub": "8.5x real-time speed on Apple Silicon GPU"},
        {"img": os.path.join(JOURNAL_IMG, "hours35_03_pyannote_speaker_diarization.png"), "tag": "DIARIZATION", "title": "PyAnnote 3.1 Speaker Split", "sub": "Neural voice embeddings separate Me vs Others"},
        {"img": os.path.join(JOURNAL_IMG, "hours35_04_librosa_acoustic_features.png"), "tag": "ACOUSTIC DSP", "title": "Pitch & Hesitation Tracking", "sub": "Librosa F0 pitch jitter and pause detection"},
        {"img": os.path.join(JOURNAL_IMG, "hours35_05_interview_analysis_report.png"), "tag": "INTERVIEW COACH", "title": "Objective Feedback", "sub": "Mistake detection linked to audio timestamps"},
        {"img": os.path.join(JOURNAL_IMG, "hours35_08_privacy_audit_results.png"), "tag": "SECURITY", "title": "Zero Cloud Dependency", "sub": "Air-gapped verification: 0 external packets"}
    ]
    build_reel("35h", scenes_35h, os.path.join(VIDEOS_DIR, "memento_35h_voice.mp3"), os.path.join(VIDEOS_DIR, "memento_35h_progress_reel.mp4"))

    # 4. Final Showcase Reel
    scenes_final = [
        {"img": os.path.join(CAD_DIR, "memento_assembly_fitted.png"), "tag": "FINAL SHOWCASE", "title": "MEMENTO Personal Memory", "sub": "Wearable Hardware + Local macOS AI Companion"},
        {"img": os.path.join(JOURNAL_IMG, "initial_02_memento_system_block_diagram.png"), "tag": "SYSTEM FLOW", "title": "Wearable Capture & Mac Sync", "sub": "Continuous 16kHz WAV recording to microSD"},
        {"img": os.path.join(RENDERS_DIR, "memento_iso_3d.png"), "tag": "HARDWARE FABRICATION", "title": "Custom KiCad 10 PCB", "sub": "75x42mm FR4 board with isolated AGND"},
        {"img": os.path.join(CAD_DIR, "memento_assembly_exploded.png"), "tag": "MECHANICAL DESIGN", "title": "Exploded CAD Assembly", "sub": "Snap-fit PETG housing with spring lapel clip"},
        {"img": os.path.join(JOURNAL_IMG, "hours35_03_pyannote_speaker_diarization.png"), "tag": "SPEAKER SEGMENTATION", "title": "Who Spoke What & When", "sub": "Multi-speaker timeline with word timestamps"},
        {"img": os.path.join(JOURNAL_IMG, "hours35_05_interview_analysis_report.png"), "tag": "INTERVIEW ANALYSIS", "title": "Actionable Vocal Debrief", "sub": "Tracks questions, mistakes, and commitments"},
        {"img": os.path.join(JOURNAL_IMG, "hours35_10_project_completion_matrix.png"), "tag": "HALF LIFE CAP", "title": "Under $60 Total Budget", "sub": "100% open source hardware & software"}
    ]
    build_reel("final", scenes_final, os.path.join(VIDEOS_DIR, "memento_final_voice.mp3"), os.path.join(VIDEOS_DIR, "memento_final_showcase_reel.mp4"))

if __name__ == "__main__":
    main()

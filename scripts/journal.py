#!/usr/bin/env python3
"""
MEMENTO Devlog Manager
----------------------
Manages devlog entries in `journal/*.md`, validates linked engineering diagrams
in `journal/images/`, guards root `JOURNAL.md` from accidental overwrites, and
helps sync/push updates to GitHub.

Usage:
    python3 scripts/journal.py status
    python3 scripts/journal.py verify
    python3 scripts/journal.py new <slug> [--hours H]
    python3 scripts/journal.py push [commit message]
"""

import sys
import os
import re
import argparse
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JOURNAL_DIR = REPO_ROOT / "journal"
IMAGES_DIR = JOURNAL_DIR / "images"
ROOT_JOURNAL = REPO_ROOT / "JOURNAL.md"

HALF_LIFE_PLACEHOLDER_SNIPPET = "Edits here are overwritten on the next sync."

def check_root_journal_guard():
    if not ROOT_JOURNAL.exists():
        return
    content = ROOT_JOURNAL.read_text(encoding="utf-8")
    if HALF_LIFE_PLACEHOLDER_SNIPPET not in content:
        print("\033[93m[WARNING] Root JOURNAL.md appears modified. Remember that Half Life's bot\n"
              "          overwrites JOURNAL.md on sync. Store local entries in journal/*.md!\033[0m\n")

def scan_entries():
    if not JOURNAL_DIR.exists():
        return []
    entries = []
    for md_file in sorted(JOURNAL_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else md_file.stem
        
        hours_match = re.search(r"\*\*(\d+)h\*\*", text) or re.search(r"(\d+)\s*hours?", text, re.IGNORECASE)
        hours = int(hours_match.group(1)) if hours_match else 0
        
        image_refs = re.findall(r"!\[(.*?)\]\((.*?)\)", text)
        words = len(re.findall(r"\b\w+\b", text))
        
        valid_images = 0
        missing_images = []
        for alt, path_str in image_refs:
            if path_str.startswith("http://") or path_str.startswith("https://"):
                valid_images += 1
                continue
            clean_path = path_str.split("?")[0].strip()
            if clean_path.startswith("journal/"):
                target = REPO_ROOT / clean_path
            elif clean_path.startswith("images/"):
                target = JOURNAL_DIR / clean_path
            else:
                target = JOURNAL_DIR / clean_path
            
            if target.exists():
                valid_images += 1
            else:
                missing_images.append(clean_path)
                
        entries.append({
            "path": md_file,
            "filename": md_file.name,
            "title": title,
            "hours": hours,
            "words": words,
            "image_refs": image_refs,
            "valid_images": valid_images,
            "missing_images": missing_images
        })
    return entries

def cmd_status(args):
    check_root_journal_guard()
    entries = scan_entries()
    print("\033[1;36m=== MEMENTO Devlog Status ===\033[0m")
    if not entries:
        print("No entries found in journal/*.md.")
        return
        
    total_hours = sum(e["hours"] for e in entries)
    total_words = sum(e["words"] for e in entries)
    total_imgs = sum(len(e["image_refs"]) for e in entries)
    
    for e in entries:
        print(f"\n\033[1m[{e['filename']}]\033[0m")
        print(f"  Title:  {e['title']}")
        print(f"  Hours:  {e['hours']}h")
        print(f"  Words:  {e['words']:,}")
        print(f"  Images: {e['valid_images']}/{len(e['image_refs'])} verified")
        if e['missing_images']:
            for m in e['missing_images']:
                print(f"    \033[91m✖ Missing: {m}\033[0m")
        else:
            print(f"    \033[92m✔ All images verified\033[0m")
            
    print("\n-------------------------------------------")
    print(f"Total Entries: {len(entries)} | Total Hours: {total_hours}h | Total Words: {total_words:,} | Total Images: {total_imgs}")
    print("-------------------------------------------")

def cmd_verify(args):
    check_root_journal_guard()
    entries = scan_entries()
    print("\033[1;34m=== Running Devlog Integrity Checks ===\033[0m")
    has_errors = False
    
    for e in entries:
        print(f"\nChecking {e['filename']}...")
        if e["missing_images"]:
            has_errors = True
            for m in e["missing_images"]:
                print(f"  \033[91m✖ Broken image link: {m}\033[0m")
        else:
            print(f"  \033[92m✔ All linked images exist on disk\033[0m")

    if has_errors:
        print("\n\033[91mVerification failed with errors.\033[0m")
        sys.exit(1)
    else:
        print("\n\033[92mAll verification checks passed successfully!\033[0m")

def main():
    parser = argparse.ArgumentParser(description="MEMENTO Devlog Manager")
    sub = parser.add_subparsers(dest="command")
    
    p_status = sub.add_parser("status", help="Show devlog summary")
    p_status.set_defaults(func=cmd_status)
    
    p_verify = sub.add_parser("verify", help="Verify image references")
    p_verify.set_defaults(func=cmd_verify)
    
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)

if __name__ == "__main__":
    main()


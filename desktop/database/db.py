"""
db.py — Local SQLite Database & FTS5 Search for MEMENTO
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.expanduser("~/Library/Application Support/Memento/memento.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Sessions
    c.execute("""
    CREATE TABLE IF NOT EXISTS recording_sessions (
        session_id TEXT PRIMARY KEY,
        start_time TEXT,
        duration_sec REAL,
        sample_rate INTEGER,
        channels INTEGER,
        bit_depth INTEGER,
        sha256 TEXT,
        title TEXT,
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Transcripts with FTS5 Full-Text Search
    c.execute("""
    CREATE TABLE IF NOT EXISTS transcripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        speaker_id TEXT,
        start_sec REAL,
        end_sec REAL,
        text TEXT,
        confidence REAL,
        FOREIGN KEY(session_id) REFERENCES recording_sessions(session_id)
    )
    """)
    
    c.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS transcripts_fts USING fts5(
        text,
        session_id UNINDEXED,
        speaker_id UNINDEXED,
        start_sec UNINDEXED,
        content='transcripts',
        content_rowid='id'
    )
    """)

    # 3. Speakers
    c.execute("""
    CREATE TABLE IF NOT EXISTS speakers (
        speaker_id TEXT PRIMARY KEY,
        label TEXT,
        speaking_ratio REAL
    )
    """)

    # 4. Commitments & Action Items
    c.execute("""
    CREATE TABLE IF NOT EXISTS commitments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        speaker_id TEXT,
        text TEXT,
        deadline TEXT,
        timestamp_sec REAL,
        is_completed INTEGER DEFAULT 0
    )
    """)

    # 5. Interview Feedback & Observations
    c.execute("""
    CREATE TABLE IF NOT EXISTS interview_observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        category TEXT,
        observation TEXT,
        evidence_sec REAL,
        quote TEXT
    )
    """)

    conn.commit()
    conn.close()

def search_transcripts(query: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT t.session_id, t.speaker_id, t.start_sec, t.end_sec, t.text,
           snippet(transcripts_fts, 0, '<b>', '</b>', '...', 15) as matched_snippet
    FROM transcripts_fts f
    JOIN transcripts t ON f.rowid = t.id
    WHERE transcripts_fts MATCH ?
    ORDER BY rank
    LIMIT 20
    """, (query,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

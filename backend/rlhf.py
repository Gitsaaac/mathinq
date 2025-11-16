# rlhf.py
import sqlite3
import json
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

DB_PATH = Path("rlhf.db")


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    conn = _get_connection()
    cur = conn.cursor()

    # One row per generated sample (video + audio + code)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS samples (
            id TEXT PRIMARY KEY,
            prompt TEXT NOT NULL,
            manim_code TEXT,
            narration_text TEXT,
            video_path TEXT,
            audio_path TEXT,
            created_at REAL NOT NULL,
            meta_json TEXT
        )
        """
    )

    # One row per feedback event (thumbs up/down etc.)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            rating INTEGER NOT NULL,          -- +1 for up, -1 for down
            comment TEXT,
            created_at REAL NOT NULL,
            meta_json TEXT,
            FOREIGN KEY(sample_id) REFERENCES samples(id)
        )
        """
    )

    conn.commit()
    conn.close()


def log_sample(
    prompt: str,
    manim_code: str,
    narration_text: Optional[str],
    video_path: str,
    audio_path: str,
    meta: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Store one generated example (what the model produced) and return a sample_id.
    You can return this sample_id to the frontend along with video/audio URLs.
    """
    sample_id = str(uuid.uuid4())
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO samples (
            id, prompt, manim_code, narration_text,
            video_path, audio_path, created_at, meta_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sample_id,
            prompt,
            manim_code,
            narration_text,
            video_path,
            audio_path,
            time.time(),
            json.dumps(meta or {}),
        ),
    )

    conn.commit()
    conn.close()
    return sample_id


def log_feedback(
    sample_id: str,
    rating: int,
    comment: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Store a feedback event for a given sample.
    rating: +1 (thumbs up) or -1 (thumbs down)
    comment: optional free-text from user
    meta: anything extra from frontend (e.g. device, duration watched)
    """
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO feedback (
            sample_id, rating, comment, created_at, meta_json
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            sample_id,
            rating,
            comment,
            time.time(),
            json.dumps(meta or {}),
        ),
    )

    conn.commit()
    conn.close()

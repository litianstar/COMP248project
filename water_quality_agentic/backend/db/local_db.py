# backend/db/local_db.py
# 简单的 SQLite 工具类 / Simple SQLite helper

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_reflections.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    """初始化数据库表 / Initialize tables if not exist."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS query_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            answer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reflection_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            answer TEXT,
            feedback TEXT,
            quality_score INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()


def log_query(query: str, answer: str = ""):
    """记录一次查询 / Log a query."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO query_log (query, answer) VALUES (?, ?);",
        (query, answer),
    )
    conn.commit()
    conn.close()


def log_reflection(query: str, answer: str, feedback: str, score: int, notes: str):
    """记录一次反思结果 / Log one reflection entry."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO reflection_log (query, answer, feedback, quality_score, notes)
        VALUES (?, ?, ?, ?, ?);
        """,
        (query, answer, feedback, score, notes),
    )
    conn.commit()
    conn.close()
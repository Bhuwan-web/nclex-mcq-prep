#!/usr/bin/env python3

import sqlite3
from typing import Dict, List, Any
from contextlib import contextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleNCLEXDatabase:
    def __init__(self, db_path: str = "nclex_simple.db"):
        self.db_path = db_path
        self.setup_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def setup_database(self):
        """Create the two simple tables."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DROP TABLE IF EXISTS questions")
                cursor.execute("DROP TABLE IF EXISTS detailed_answers")
                # Questions table - just questions and options
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        page_number INTEGER NOT NULL,
                        question_number INTEGER NOT NULL,
                        question_text TEXT NOT NULL,
                        option_a TEXT NOT NULL,
                        option_b TEXT NOT NULL,
                        option_c TEXT NOT NULL,
                        option_d TEXT NOT NULL,
                        quick_answer_page INTEGER,
                        detailed_answer_page INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Detailed answers table - answers with rationales
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS detailed_answers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        page_number INTEGER NOT NULL,
                        question_number INTEGER NOT NULL,
                        answer CHAR(1) NOT NULL,
                        rationale TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                conn.commit()
                logger.info("Simple database setup completed")
        except sqlite3.Error as e:
            logger.error(f"Error setting up database: {e}")
            raise

    def insert_question(self, question_data: Dict[str, Any]):
        """Insert a question."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO questions 
                (page_number, question_number, question_text, option_a, option_b, option_c, option_d,
                 quick_answer_page, detailed_answer_page)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    question_data["page_number"],
                    question_data["question_number"],
                    question_data["question_text"],
                    question_data["option_a"],
                    question_data["option_b"],
                    question_data["option_c"],
                    question_data["option_d"],
                    question_data.get("quick_answer_page"),
                    question_data.get("detailed_answer_page"),
                ),
            )
            conn.commit()

    def insert_detailed_answer(
        self,
        page_number: int,
        question_number: int,
        answer: str,
        rationale: str,
    ):
        """Insert a detailed answer."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO detailed_answers (page_number, question_number, answer, rationale)
                VALUES (?, ?, ?, ?)
            """,
                (
                    page_number,
                    question_number,
                    answer,
                    rationale,
                ),
            )
            conn.commit()

    def batch_insert_detailed_answers(self, answers: List[Dict]):
        """Batch insert detailed answers."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """
                INSERT OR REPLACE INTO detailed_answers (page_number, question_number, answer, rationale)
                VALUES (?, ?, ?, ?)
            """,
                [
                    (
                        a["page_number"],
                        a["question_number"],
                        a["answer"],
                        a["rationale"],
                    )
                    for a in answers
                ],
            )
            conn.commit()
            logger.info(f"Batch inserted {len(answers)} detailed answers")

    def get_stats(self):
        """Get database statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM questions")
            questions_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM detailed_answers")
            detailed_answers_count = cursor.fetchone()[0]

            return {
                "questions": questions_count,
                "detailed_answers": detailed_answers_count,
            }

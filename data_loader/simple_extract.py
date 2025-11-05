#!/usr/bin/env python3

import pdfplumber
import re
from typing import Dict, List, Optional, Any
from simple_nclex_db import SimpleNCLEXDatabase
import json


class SimpleNCLEXExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.db = SimpleNCLEXDatabase()

    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        # Remove reference lines and normalize whitespace
        text = re.sub(r"CN:\s*.*?(?=\n|$)", "", text)
        text = re.sub(r"Client Needs.*?(?=\n|$)", "", text, re.IGNORECASE)
        # Remove Quick Answer and Detailed Answer reference lines
        text = re.sub(r"Quick Answer:\s*\d+", "", text, re.IGNORECASE)
        text = re.sub(r"Detailed Answer:\s*\d+", "", text, re.IGNORECASE)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def extract_questions_from_page(self, page_num: int, page_text: str) -> List[Dict]:
        """Extract all questions from a single page."""
        questions = []

        # Split by question numbers - look for number at start of line or after whitespace
        question_blocks = re.split(r"(?=(?:^|\n)\s*\d+\.)", page_text)

        for block in question_blocks:
            if not block.strip():
                continue

            # Extract question number and text - handle whitespace at start
            question_match = re.search(r"^\s*(\d+)\.\s+(.*?)(?=❍\s*A\.)", block, re.DOTALL)
            if not question_match:
                continue

            question_number = int(question_match.group(1))
            question_text = self.clean_text(question_match.group(2))

            # Debug: Print question numbers to verify parsing
            if question_number <= 10 or question_number % 50 == 0:
                print(f"  Parsed question {question_number}: {question_text[:50]}...")

            # Extract options
            options = {}
            option_pattern = r"❍\s*([A-D])\.\s*(.*?)(?=(?:\n❍\s*[A-D]\.|\n\d+\.|\Z))"

            for option_match in re.finditer(option_pattern, block, re.DOTALL):
                letter = option_match.group(1)
                option_text = self.clean_text(option_match.group(2))
                options[letter] = option_text

            # Only add if we have all 4 options and valid question number (1-250)
            if len(options) == 4 and 1 <= question_number <= 250:
                # Extract page references using the same patterns as extract_questions.py
                quick_answer_page = None
                detailed_answer_page = None

                # Look for "Quick Answer: 54" pattern
                quick_match = re.search(r"Quick Answer:\s*(\d+)", block, re.IGNORECASE)
                if quick_match:
                    quick_answer_page = int(quick_match.group(1))

                # Look for "Detailed Answer: 78" pattern
                detailed_match = re.search(r"Detailed Answer:\s*(\d+)", block, re.IGNORECASE)
                if detailed_match:
                    detailed_answer_page = int(detailed_match.group(1)) + 20

                questions.append(
                    {
                        "page_number": page_num,
                        "question_number": question_number,
                        "question_text": question_text,
                        "option_a": options.get("A", ""),
                        "option_b": options.get("B", ""),
                        "option_c": options.get("C", ""),
                        "option_d": options.get("D", ""),
                        "quick_answer_page": quick_answer_page,
                        "detailed_answer_page": detailed_answer_page,
                    }
                )

        return questions

    def extract_detailed_answers_from_page(self, page_num: int, page_text: str) -> List[Dict]:
        """Extract detailed answers from a page."""
        answers = []

        # Pattern for "1. Answer B is correct. Rationale..." - handle multi-digit numbers
        pattern = r"(?:^|\n)\s*(\d+)\.\s*Answer\s+([A-D])\s+is\s+correct\.\s*(.*?)(?=(?:^|\n)\s*\d+\.\s*Answer\s+[A-D]\s+is\s+correct|$)"

        matches = re.findall(pattern, page_text, re.DOTALL | re.IGNORECASE)

        for q_num, answer, rationale in matches:
            try:
                question_num = int(q_num)
                clean_rationale = self.clean_text(rationale)

                if (
                    len(clean_rationale) > 10 and 1 <= question_num <= 250
                ):  # Must have substantial rationale and valid question number
                    answers.append(
                        {
                            "page_number": page_num,
                            "question_number": question_num,
                            "answer": answer.upper(),
                            "rationale": clean_rationale,
                        }
                    )
            except ValueError:
                continue

        return answers

    def scan_for_questions(self, start_page: int = 1, end_page: int = None):
        """First scan: Extract all questions."""
        print("=== SCANNING FOR QUESTIONS ===")

        with pdfplumber.open(self.pdf_path) as pdf:
            if end_page is None:
                end_page = len(pdf.pages)

            total_questions = 0

            for page_num in range(start_page, min(end_page + 1, len(pdf.pages) + 1)):
                page = pdf.pages[page_num - 1]  # Convert to 0-based
                text = page.extract_text()

                if not text:
                    continue

                questions = self.extract_questions_from_page(page_num, text)

                if questions:
                    print(f"Page {page_num}: Found {len(questions)} questions")
                    for question in questions:
                        self.db.insert_question(question)
                    total_questions += len(questions)

            print(f"Total questions extracted: {total_questions}")

    def scan_for_detailed_answers(self, start_page: int = 1, end_page: int = None):
        """Third scan: Extract detailed answers."""
        print("\n=== SCANNING FOR DETAILED ANSWERS ===")

        with pdfplumber.open(self.pdf_path) as pdf:
            if end_page is None:
                end_page = len(pdf.pages)

            total_answers = 0

            for page_num in range(start_page, min(end_page + 1, len(pdf.pages) + 1)):
                page = pdf.pages[page_num - 1]  # Convert to 0-based
                text = page.extract_text()

                if not text:
                    continue

                answers = self.extract_detailed_answers_from_page(page_num, text)

                if answers:
                    print(f"Page {page_num}: Found {len(answers)} detailed answers")
                    self.db.batch_insert_detailed_answers(answers)
                    total_answers += len(answers)

            print(f"Total detailed answers extracted: {total_answers}")

    def process_full_pdf(self, start_page: int = 1, end_page: int = None):
        """Process the entire PDF in three passes."""
        print(f"Processing PDF: {self.pdf_path}")
        print(f"Pages: {start_page} to {end_page or 'end'}")

        # Pass 1: Questions
        self.scan_for_questions(start_page, end_page)

        # Pass 3: Detailed answers
        self.scan_for_detailed_answers(start_page, end_page)

        # Show final stats
        stats = self.db.get_stats()
        print(f"\n=== FINAL STATISTICS ===")
        print(f"Questions: {stats['questions']}")
        print(f"Detailed answers: {stats['detailed_answers']}")

        return stats


if __name__ == "__main__":
    extractor = SimpleNCLEXExtractor("nclex.pdf")

    # Process the entire PDF
    stats = extractor.process_full_pdf(start_page=21)  # Start from page 21

    print("\nProcessing complete!")

#!/usr/bin/env python3
"""Test script to demonstrate the NCLEX question extraction functionality."""

from nclex_db import NCLEXDatabase
from extract_questions import NCLEXQuestionExtractor


def test_database_functionality():
    """Test the database functionality with extracted questions."""
    print("=== Testing Database Functionality ===")

    db = NCLEXDatabase()

    # Get all questions
    all_questions = db.get_all_questions(chapter=1)
    print(f"Total questions in database: {len(all_questions)}")

    if all_questions:
        # Show a few examples
        for i, question in enumerate(all_questions[:3]):
            print(f"\n--- Question {question['number']} ---")
            print(f"Text: {question['question'][:80]}...")
            print(f"Options: A) {question['options']['A'][:50]}...")
            print(f"         B) {question['options']['B'][:50]}...")
            print(f"         C) {question['options']['C'][:50]}...")
            print(f"         D) {question['options']['D'][:50]}...")

            if question.get("quick_answer"):
                print(f"Quick Answer: {question['quick_answer']}")

            if question.get("detailed_answer") and question["detailed_answer"]:
                print(f"Detailed Answer: {question['detailed_answer']['answer']}")
                if question["detailed_answer"].get("rationale"):
                    print(f"Rationale: {question['detailed_answer']['rationale'][:100]}...")

    # Statistics
    questions_with_quick = sum(1 for q in all_questions if q.get("quick_answer"))
    questions_with_detailed = sum(1 for q in all_questions if q.get("detailed_answer"))

    print(f"\n=== Statistics ===")
    print(f"Questions with quick answers: {questions_with_quick}/{len(all_questions)}")
    print(f"Questions with detailed answers: {questions_with_detailed}/{len(all_questions)}")
    print(
        f"Coverage: {(questions_with_quick/len(all_questions)*100):.1f}% quick, {(questions_with_detailed/len(all_questions)*100):.1f}% detailed"
    )


if __name__ == "__main__":
    test_database_functionality()

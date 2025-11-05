# NCLEX MCQ Practice API

A comprehensive FastAPI application for practicing NCLEX multiple choice questions with tracking, reporting, and mistake analysis.

## Features

-   **Question Practice**: Get paginated questions (10 per page)
-   **Answer Submission**: Submit answers and get immediate scoring
-   **Mistake Tracking**: Track frequently missed questions
-   **Performance Reports**: View overall accuracy and session statistics
-   **Practice Sessions**: Review past practice sessions
-   **Detailed Answers**: Get explanations and rationales for questions

## API Endpoints

### Questions

-   `GET /questions/?page=1` - Get paginated questions for practice
-   `GET /questions-with-answers/?page=1` - Get questions with their detailed answers
-   `GET /question/{question_id}/answer/` - Get detailed answer for a specific question

### Practice & Submission

-   `POST /submit/` - Submit answers for a practice session
-   `GET /practice-mistakes/?limit=10` - Get most frequently missed questions

### Reports & Analytics

-   `GET /report/` - Get overall performance statistics
-   `GET /sessions/?limit=10` - Get recent practice sessions
-   `GET /mistakes/` - Get all mistakes with question details
-   `GET /stats/` - Get database statistics

### Web Interface

-   `GET /` - Main web interface for practicing questions
-   `GET /docs` - Interactive API documentation

## Setup & Installation

1. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2. **Ensure database exists:**
   Make sure `nclex_simple.db` exists in the parent directory (created by running the extraction scripts)

3. **Run the API:**

    ```bash
    python run.py
    ```

4. **Access the application:**
    - Web Interface: http://localhost:8000
    - API Documentation: http://localhost:8000/docs
    - API Base URL: http://localhost:8000

## Database Schema

The API uses two main tables:

### Questions Table

-   Stores questions with options and page references
-   Fields: id, page_number, question_number, question_text, option_a/b/c/d, quick_answer_page, detailed_answer_page

### Detailed Answers Table

-   Stores correct answers with rationales
-   Fields: id, page_number, question_number, answer, rationale

### Practice Tables

-   `practice_sessions`: Tracks each practice session
-   `practice_answers`: Individual answers within sessions
-   `mistakes`: Tracks frequently missed questions

## Usage Examples

### Start a Practice Session

1. Visit http://localhost:8000
2. Click "Start Practice (10 Questions)"
3. Answer the questions
4. Click "Submit Answers" to see your score

### Practice Your Mistakes

1. Click "Practice Mistakes" to focus on questions you've gotten wrong
2. These are ordered by frequency of mistakes

### View Performance

1. Click "View Report" to see overall statistics
2. Click "View Sessions" to see recent practice sessions

## API Usage

### Get Questions (Python example)

```python
import requests

# Get first page of questions
response = requests.get("http://localhost:8000/questions/?page=1")
questions = response.json()

# Submit answers
answers = [
    {"question_id": 1, "user_answer": "A"},
    {"question_id": 2, "user_answer": "B"}
]
response = requests.post("http://localhost:8000/submit/", json=answers)
result = response.json()
print(f"Score: {result['score']}/{result['total']}")
```

## Features

### Smart Question Selection

-   Questions are served with proper pagination
-   Mistake-based practice focuses on weak areas
-   Questions include page references for answer lookup

### Comprehensive Tracking

-   Every answer is tracked for performance analysis
-   Mistakes are counted and can be practiced specifically
-   Session history is maintained

### Rich Reporting

-   Overall accuracy percentage
-   Session-by-session performance
-   Most frequently missed questions
-   Database statistics

## Development

The API is built with:

-   **FastAPI**: Modern, fast web framework
-   **SQLAlchemy**: Database ORM
-   **Pydantic**: Data validation
-   **SQLite**: Lightweight database

To extend the API, modify the relevant files:

-   `models.py`: Database models
-   `schemas.py`: API request/response schemas
-   `main.py`: API endpoints
-   `db.py`: Database configuration

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import SessionLocal, init_db
from .models import Question, PracticeSession, PracticeAnswer, Mistake, DetailedAnswer
from .schemas import (
    QuestionSchema,
    PracticeAnswerSchema,
    PracticeSessionSchema,
    MistakeSchema,
    OptionSchema,
    DetailedAnswerSchema,
    MCQWithAnswerSchema,
)
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI(
    title="NCLEX MCQ Practice API",
    description="API for practicing NCLEX multiple choice questions",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def read_root():
    """Serve the main HTML page."""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "NCLEX MCQ Practice API", "docs": "/docs"}


@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "message": "API is running"}


@app.get("/questions/", response_model=List[QuestionSchema])
def get_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    # If offset is provided, use it directly; otherwise calculate from page
    if offset > 0:
        actual_offset = offset
    else:
        actual_offset = (page - 1) * page_size

    questions = (
        db.query(Question).order_by(Question.id).offset(actual_offset).limit(page_size).all()
    )
    result = []
    for q in questions:
        result.append(
            QuestionSchema(
                id=q.id,
                page_number=q.page_number,
                question_number=q.question_number,
                question_text=q.question_text,
                options=OptionSchema(A=q.option_a, B=q.option_b, C=q.option_c, D=q.option_d),
                quick_answer_page=q.quick_answer_page,
                detailed_answer_page=q.detailed_answer_page,
            )
        )
    return result


@app.post("/submit/", response_model=PracticeSessionSchema)
def submit_answers(answers: List[PracticeAnswerSchema], db: Session = Depends(get_db)):
    session = PracticeSession(started_at=datetime.utcnow(), score=0, total=len(answers))
    db.add(session)
    db.commit()
    db.refresh(session)
    score = 0
    for ans in answers:
        q = db.query(Question).filter(Question.id == ans.question_id).first()
        if not q:
            continue

        # Find the correct answer from detailed_answers table
        detailed_answer = (
            db.query(DetailedAnswer)
            .filter(
                DetailedAnswer.page_number == q.page_number,
                DetailedAnswer.question_number == q.question_number,
            )
            .first()
        )

        is_correct = detailed_answer and (
            ans.user_answer.upper() == detailed_answer.answer.upper()
        )

        pa = PracticeAnswer(
            session_id=session.id,
            question_id=ans.question_id,
            user_answer=ans.user_answer,
            is_correct=is_correct,
        )
        db.add(pa)

        if not is_correct:
            mistake = db.query(Mistake).filter(Mistake.question_id == ans.question_id).first()
            if mistake:
                mistake.wrong_count += 1
                mistake.last_wrong = datetime.utcnow()
            else:
                mistake = Mistake(
                    question_id=ans.question_id, wrong_count=1, last_wrong=datetime.utcnow()
                )
                db.add(mistake)
        else:
            score += 1

    session.score = score
    db.commit()
    db.refresh(session)

    session_answers = (
        db.query(PracticeAnswer).filter(PracticeAnswer.session_id == session.id).all()
    )
    return PracticeSessionSchema(
        id=session.id,
        started_at=session.started_at.isoformat(),
        score=session.score,
        total=session.total,
        answers=[
            PracticeAnswerSchema(question_id=a.question_id, user_answer=a.user_answer)
            for a in session_answers
        ],
    )


@app.get("/report/")
def get_report(db: Session = Depends(get_db)):
    total = db.query(PracticeAnswer).count()
    correct = db.query(PracticeAnswer).filter(PracticeAnswer.is_correct == True).count()
    wrong = db.query(PracticeAnswer).filter(PracticeAnswer.is_correct == False).count()

    # Get session statistics
    sessions = db.query(PracticeSession).all()
    total_sessions = len(sessions)
    avg_score = sum(s.score for s in sessions) / total_sessions if total_sessions > 0 else 0

    return {
        "total_questions_answered": total,
        "correct_answers": correct,
        "wrong_answers": wrong,
        "accuracy_percentage": round(correct / total * 100, 2) if total > 0 else 0,
        "total_sessions": total_sessions,
        "average_score": round(avg_score, 2),
    }


@app.get("/mistakes/", response_model=List[MistakeSchema])
def get_mistakes(db: Session = Depends(get_db)):
    mistakes = db.query(Mistake).order_by(Mistake.wrong_count.desc()).all()
    result = []
    for m in mistakes:
        q = m.question
        result.append(
            MistakeSchema(
                question_id=m.question_id,
                wrong_count=m.wrong_count,
                last_wrong=m.last_wrong.isoformat(),
                question=QuestionSchema(
                    id=q.id,
                    page_number=q.page_number,
                    question_number=q.question_number,
                    question_text=q.question_text,
                    options=OptionSchema(A=q.option_a, B=q.option_b, C=q.option_c, D=q.option_d),
                    quick_answer_page=q.quick_answer_page,
                    detailed_answer_page=q.detailed_answer_page,
                ),
            )
        )
    return result


@app.get("/questions-with-answers/", response_model=List[MCQWithAnswerSchema])
def get_questions_with_answers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    # If offset is provided, use it directly; otherwise calculate from page
    if offset > 0:
        actual_offset = offset
    else:
        actual_offset = (page - 1) * page_size

    questions = (
        db.query(Question).order_by(Question.id).offset(actual_offset).limit(page_size).all()
    )
    result = []
    for q in questions:
        detailed_answer = (
            db.query(DetailedAnswer)
            .filter(
                DetailedAnswer.page_number == q.page_number,
                DetailedAnswer.question_number == q.question_number,
            )
            .first()
        )
        result.append(
            MCQWithAnswerSchema(
                question=QuestionSchema(
                    id=q.id,
                    page_number=q.page_number,
                    question_number=q.question_number,
                    question_text=q.question_text,
                    options=OptionSchema(A=q.option_a, B=q.option_b, C=q.option_c, D=q.option_d),
                    quick_answer_page=q.quick_answer_page,
                    detailed_answer_page=q.detailed_answer_page,
                ),
                detailed_answer=(
                    DetailedAnswerSchema(
                        id=detailed_answer.id,
                        page_number=detailed_answer.page_number,
                        question_number=detailed_answer.question_number,
                        answer=detailed_answer.answer,
                        rationale=detailed_answer.rationale,
                    )
                    if detailed_answer
                    else None
                ),
            )
        )
    return result


@app.get("/practice-mistakes/", response_model=List[QuestionSchema])
def get_practice_mistakes(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Get questions that were answered incorrectly most frequently for practice."""
    mistakes = db.query(Mistake).order_by(Mistake.wrong_count.desc()).limit(limit).all()
    result = []
    for m in mistakes:
        q = m.question
        result.append(
            QuestionSchema(
                id=q.id,
                page_number=q.page_number,
                question_number=q.question_number,
                question_text=q.question_text,
                options=OptionSchema(A=q.option_a, B=q.option_b, C=q.option_c, D=q.option_d),
                quick_answer_page=q.quick_answer_page,
                detailed_answer_page=q.detailed_answer_page,
            )
        )
    return result


@app.get("/sessions/", response_model=List[PracticeSessionSchema])
def get_practice_sessions(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get recent practice sessions."""
    sessions = (
        db.query(PracticeSession).order_by(PracticeSession.started_at.desc()).limit(limit).all()
    )
    result = []
    for session in sessions:
        session_answers = (
            db.query(PracticeAnswer).filter(PracticeAnswer.session_id == session.id).all()
        )
        result.append(
            PracticeSessionSchema(
                id=session.id,
                started_at=session.started_at.isoformat(),
                score=session.score,
                total=session.total,
                answers=[
                    PracticeAnswerSchema(question_id=a.question_id, user_answer=a.user_answer)
                    for a in session_answers
                ],
            )
        )
    return result


@app.get("/question/{question_id}/answer", response_model=DetailedAnswerSchema)
def get_question_answer(question_id: int, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    # Join on question_number and page_number
    detailed_answer = (
        db.query(DetailedAnswer)
        .filter(
            DetailedAnswer.page_number == q.detailed_answer_page,
            DetailedAnswer.question_number == q.question_number,
        )
        .first()
    )
    if not detailed_answer:
        raise HTTPException(status_code=404, detail="Detailed answer not found")
    return DetailedAnswerSchema(
        id=detailed_answer.id,
        page_number=detailed_answer.page_number,
        question_number=detailed_answer.question_number,
        answer=detailed_answer.answer,
        rationale=detailed_answer.rationale,
    )


@app.get("/stats/")
def get_stats(db: Session = Depends(get_db)):
    """Get database statistics."""
    total_questions = db.query(Question).count()
    total_answers = db.query(DetailedAnswer).count()
    total_sessions = db.query(PracticeSession).count()
    total_mistakes = db.query(Mistake).count()

    return {
        "total_questions": total_questions,
        "total_answers": total_answers,
        "total_practice_sessions": total_sessions,
        "unique_mistakes": total_mistakes,
    }


@app.get("/questions/count")
def get_question_count(db: Session = Depends(get_db)):
    """Get total number of questions available."""
    return {"total_questions": db.query(Question).count()}

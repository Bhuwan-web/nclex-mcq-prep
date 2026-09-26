from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .db import SessionLocal, init_db
from .models import Question, PracticeSession, PracticeAnswer, DetailedAnswer, User, UserMistake
from .schemas import (
    QuestionSchema,
    PracticeAnswerSchema,
    PracticeAnswerWithFeedbackSchema,
    PracticeSessionSchema,
    PracticeSessionWithFeedbackSchema,
    MistakeSchema,
    OptionSchema,
    DetailedAnswerSchema,
    MCQWithAnswerSchema,
)
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import re
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from .auth import create_access_token, get_current_user, password_hash

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


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    id: int
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.post("/auth/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(status_code=422, detail="A valid email address is required")
    user = User(email=email, password_hash=password_hash.hash(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    db.refresh(user)
    return UserPublic(id=user.id, email=user.email)


@app.post("/auth/token", response_model=TokenResponse)
def login_user(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form.username.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None or not password_hash.verify(form.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user))


@app.get("/auth/me", response_model=UserPublic)
def read_current_user(user: User = Depends(get_current_user)):
    return UserPublic(id=user.id, email=user.email)


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


@app.post("/submit/", response_model=PracticeSessionWithFeedbackSchema)
def submit_answers(
    answers: List[PracticeAnswerSchema],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit practice answers and get detailed feedback with explanations."""
    session = PracticeSession(
        started_at=datetime.utcnow(), score=0, total=len(answers), user_id=user.id
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    score = 0
    feedback_answers = []

    for ans in answers:
        # Get question details
        q = db.query(Question).filter(Question.id == ans.question_id).first()
        if not q:
            continue

        # Find the correct answer from detailed_answers table
        detailed_answer = (
            db.query(DetailedAnswer)
            .filter(
                Question.page_number == ans.page_number,
                DetailedAnswer.question_number == ans.question_number,
            )
            .first()
        )

        is_correct = detailed_answer and (
            ans.user_answer.upper() == detailed_answer.answer.upper()
        )
        correct_answer = detailed_answer.answer if detailed_answer else "N/A"

        # Save practice answer
        pa = PracticeAnswer(
            session_id=session.id,
            question_id=ans.question_id,
            user_answer=ans.user_answer,
            is_correct=is_correct,
        )
        db.add(pa)

        # Track mistakes
        if not is_correct:
            mistake = (
                db.query(UserMistake)
                .filter(UserMistake.user_id == user.id, UserMistake.question_id == ans.question_id)
                .first()
            )
            if mistake:
                mistake.wrong_count += 1
                mistake.last_wrong = datetime.utcnow()
            else:
                mistake = UserMistake(
                    user_id=user.id,
                    question_id=ans.question_id,
                    wrong_count=1,
                    last_wrong=datetime.utcnow(),
                )
                db.add(mistake)
        else:
            score += 1

        # Prepare feedback data
        feedback_answers.append(
            PracticeAnswerWithFeedbackSchema(
                question_id=ans.question_id,
                question_number=ans.question_number,
                page_number=ans.page_number,
                user_answer=ans.user_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
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

    # Update session with final score
    session.score = score
    accuracy_percentage = round((score / len(answers)) * 100, 2) if answers else 0
    db.commit()
    db.refresh(session)

    return PracticeSessionWithFeedbackSchema(
        id=session.id,
        started_at=session.started_at.isoformat(),
        score=session.score,
        total=session.total,
        accuracy_percentage=accuracy_percentage,
        answers=feedback_answers,
    )


@app.get("/report/")
def get_report(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user_answers = db.query(PracticeAnswer).join(PracticeSession).filter(PracticeSession.user_id == user.id)
    total = user_answers.count()
    correct = user_answers.filter(PracticeAnswer.is_correct.is_(True)).count()
    wrong = user_answers.filter(PracticeAnswer.is_correct.is_(False)).count()

    # Get session statistics
    sessions = db.query(PracticeSession).filter(PracticeSession.user_id == user.id).all()
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
def get_mistakes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    mistakes = (
        db.query(UserMistake)
        .filter(UserMistake.user_id == user.id)
        .order_by(UserMistake.wrong_count.desc())
        .all()
    )
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
def get_practice_mistakes(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get questions that were answered incorrectly most frequently for practice."""
    mistakes = (
        db.query(UserMistake)
        .filter(UserMistake.user_id == user.id)
        .order_by(UserMistake.wrong_count.desc())
        .limit(limit)
        .all()
    )
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
def get_practice_sessions(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get recent practice sessions."""
    sessions = (
        db.query(PracticeSession)
        .filter(PracticeSession.user_id == user.id)
        .order_by(PracticeSession.started_at.desc())
        .limit(limit)
        .all()
    )
    result = []
    for session in sessions:
        session_answers = (
            db.query(PracticeAnswer).filter(PracticeAnswer.session_id == session.id).all()
        )
        # Get question details for each answer
        enhanced_answers = []
        for a in session_answers:
            q = db.query(Question).filter(Question.id == a.question_id).first()
            if q:
                enhanced_answers.append(
                    PracticeAnswerSchema(
                        question_id=a.question_id,
                        question_number=q.question_number,
                        page_number=q.page_number,
                        user_answer=a.user_answer,
                    )
                )

        accuracy_percentage = (
            round((session.score / session.total) * 100, 2) if session.total > 0 else 0
        )
        result.append(
            PracticeSessionSchema(
                id=session.id,
                started_at=session.started_at.isoformat(),
                score=session.score,
                total=session.total,
                accuracy_percentage=accuracy_percentage,
                answers=enhanced_answers,
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
def get_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get database statistics."""
    total_questions = db.query(Question).count()
    total_answers = db.query(DetailedAnswer).count()
    total_sessions = db.query(PracticeSession).filter(PracticeSession.user_id == user.id).count()
    total_mistakes = db.query(UserMistake).filter(UserMistake.user_id == user.id).count()

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

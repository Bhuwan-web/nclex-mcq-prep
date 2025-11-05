from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    CHAR,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    page_number = Column(Integer, nullable=False)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    quick_answer_page = Column(Integer)
    detailed_answer_page = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("page_number", "question_number", name="_page_qnum_uc"),)


class DetailedAnswer(Base):
    __tablename__ = "detailed_answers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    page_number = Column(Integer, nullable=False)
    question_number = Column(Integer, nullable=False)
    answer = Column(CHAR(1), nullable=False)
    rationale = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        UniqueConstraint("page_number", "question_number", name="_page_qnum_ans_uc"),
    )


class PracticeSession(Base):
    __tablename__ = "practice_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    score = Column(Integer, default=0)
    total = Column(Integer, default=0)


class PracticeAnswer(Base):
    __tablename__ = "practice_answers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(String(1), nullable=False)
    is_correct = Column(Boolean, default=False)
    session = relationship("PracticeSession", backref="answers")
    question = relationship("Question")


class Mistake(Base):
    __tablename__ = "mistakes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"), unique=True)
    wrong_count = Column(Integer, default=1)
    last_wrong = Column(DateTime, default=datetime.utcnow)
    question = relationship("Question")

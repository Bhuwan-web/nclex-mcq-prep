from pydantic import BaseModel
from typing import List, Optional


class OptionSchema(BaseModel):
    A: str
    B: str
    C: str
    D: str


class QuestionSchema(BaseModel):
    id: int
    page_number: int
    question_number: int
    question_text: str
    options: OptionSchema
    quick_answer_page: Optional[int] = None
    detailed_answer_page: Optional[int] = None


class DetailedAnswerSchema(BaseModel):
    id: int
    page_number: int
    question_number: int
    answer: str
    rationale: str


class MCQWithAnswerSchema(BaseModel):
    question: QuestionSchema
    detailed_answer: Optional[DetailedAnswerSchema]


class PracticeAnswerSchema(BaseModel):
    question_id: int
    user_answer: str


class PracticeSessionSchema(BaseModel):
    id: int
    started_at: str
    score: int
    total: int
    answers: List[PracticeAnswerSchema]


class MistakeSchema(BaseModel):
    question_id: int
    wrong_count: int
    last_wrong: str
    question: QuestionSchema

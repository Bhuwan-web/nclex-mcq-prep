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
    question_number: int
    page_number: int
    user_answer: str


class PracticeAnswerWithFeedbackSchema(BaseModel):
    question_id: int
    question_number: int
    page_number: int
    user_answer: str
    correct_answer: str
    is_correct: bool
    question: QuestionSchema
    detailed_answer: Optional[DetailedAnswerSchema]


class PracticeSessionSchema(BaseModel):
    id: int
    started_at: str
    score: int
    total: int
    accuracy_percentage: float
    answers: List[PracticeAnswerSchema]


class PracticeSessionWithFeedbackSchema(BaseModel):
    id: int
    started_at: str
    score: int
    total: int
    accuracy_percentage: float
    answers: List[PracticeAnswerWithFeedbackSchema]


class MistakeSchema(BaseModel):
    question_id: int
    wrong_count: int
    last_wrong: str
    question: QuestionSchema

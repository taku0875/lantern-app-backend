from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import List, Optional

# --- APIリクエストボディ ---
class MoodData(BaseModel):
    user_id: int
    answers: List['AnswerData']

class AnswerData(BaseModel):
    question_id: int
    answer_choice: int

class LoginRequest(BaseModel):
    email: str
    password: str

# 【修正】RegisterRequestをDBのuserテーブルに合わせて修正
class RegisterRequest(BaseModel):
    user_id: str # ログインIDとして使用
    name: str
    email: str
    password: str
    prefecture: Optional[str] = None
    birthday: Optional[date] = None
    gender: Optional[str] = None

# --- APIレスポンス ---
class Question(BaseModel):
    question_id: int
    category_id: int
    question_text: str
    model_config = ConfigDict(from_attributes=True)

class QuestionsResponse(BaseModel):
    questions: List[Question]
    message: str

class LoginResponse(BaseModel):
    message: str
    user: dict
    token: str

class RegisterResponse(BaseModel):
    message: str
    user: dict
    token: str

# MoodDataがAnswerDataを前方参照できるように更新
MoodData.model_rebuild()

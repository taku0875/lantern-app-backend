import hashlib
import secrets
from datetime import datetime
from typing import List
import math
import random

from fastapi import FastAPI, Depends, HTTPException, Query, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
auth_router = APIRouter(prefix="/api/auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 【修正】色計算ロジックを平均点に戻しました
def generate_color_id_from_answers(answers: List[schemas.AnswerData]) -> int:
    """
    回答データのリストから平均スコアを算出し、対応するcolor_idを返す
    """
    if not answers:
        return 3  # デフォルトは「普通」のcolor_id

    scores = [ans.answer_choice for ans in answers]
    avg_score = sum(scores) / len(scores)

    # 平均スコアに応じたcolor_idを返す (1-5の5段階評価)
    if avg_score >= 4.5:
        return 5 # とても良い
    if avg_score >= 3.5:
        return 4 # 良い
    if avg_score >= 2.5:
        return 3 # 普通
    if avg_score >= 1.5:
        return 2 # やや心配
    return 1 # 心配

# --- DBと連携するAPI ---

@app.post("/mood/save")
async def save_mood(mood_data: schemas.MoodData, db: Session = Depends(get_db)):
    color_id = generate_color_id_from_answers(mood_data.answers)
    crud.save_daily_record_to_db(db, mood_data=mood_data, color_id=color_id)
    return {"message": "Mood saved", "color_id": color_id}

@app.get("/mood/week")
async def get_weekly_colors(user_id: int, db: Session = Depends(get_db)):
    weekly_data = crud.get_weekly_records_from_db(db, user_id=user_id)
    color_ids = [record.color_id for record in weekly_data]
    return {"color_ids": color_ids}

@app.get("/api/questions", response_model=schemas.QuestionsResponse)
def get_questions(db: Session = Depends(get_db)):
    questions_from_db = crud.get_questions_from_db(db)
    questions_schema = [schemas.Question.model_validate(q) for q in questions_from_db]
    return schemas.QuestionsResponse(questions=questions_schema, message="質問を正常に取得しました")

@app.post("/suggested-actions")
def get_suggested_actions(req: schemas.ActionRequest):
    score = req.score
    # ... (この部分は変更なし) ...
    return {"message": "suggested-actions not fully implemented"}

# --- 認証API ---

@auth_router.post("/register", response_model=schemas.RegisterResponse)
def register(register_data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=register_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="このメールアドレスは既に使用されています")
    
    hashed_password = hashlib.sha256(register_data.password.encode()).hexdigest()
    new_user = crud.create_user(db, user_data=register_data, hashed_password=hashed_password)
    
    token = secrets.token_urlsafe(32)
    user_info = {"id": new_user.user_id, "name": new_user.name, "email": new_user.email}
    return schemas.RegisterResponse(message="会員登録が完了しました", user=user_info, token=token)

@auth_router.post("/login", response_model=schemas.LoginResponse)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    hashed_password = hashlib.sha256(login_data.password.encode()).hexdigest()
    user = crud.get_user_by_email(db, email=login_data.email)

    if not user or user.password != hashed_password:
        raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが間違っています")

    token = secrets.token_urlsafe(32)
    user_info = {"id": user.user_id, "name": user.name, "email": user.email}
    return schemas.LoginResponse(message="ログインに成功しました", user=user_info, token=token)

app.include_router(auth_router)

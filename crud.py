from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional
import models
import schemas

# 【追加】新規ユーザーを作成する関数
def create_user(db: Session, user_data: schemas.RegisterRequest, hashed_password: str):
    new_user = models.User(
        user_id=user_data.user_id,
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        prefecture=user_data.prefecture,
        birthday=user_data.birthday,
        gender=user_data.gender
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """メールアドレスでユーザーを検索する"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_questions_from_db(db: Session) -> List[models.Question]:
    """DBから各カテゴリの質問をランダムに1問ずつ取得する"""
    subquery = db.query(
        models.Question,
        func.row_number().over(
            partition_by=models.Question.category_id,
            order_by=func.rand()
        ).label('row_num')
    ).subquery()
    questions = db.query(subquery).filter(subquery.c.row_num == 1).all()
    return questions

def get_weekly_records_from_db(db: Session, user_id: int) -> List[models.DailyRecord]:
    """DBから直近7日間の記録を取得する"""
    today = datetime.now().date()
    one_week_ago = today - timedelta(days=7)
    return db.query(models.DailyRecord).filter(
        models.DailyRecord.user_id == user_id,
        models.DailyRecord.check_in_date >= one_week_ago
    ).order_by(models.DailyRecord.check_in_date).all()

def save_daily_record_to_db(db: Session, mood_data: schemas.MoodData, color_id: int):
    """日々の記録と回答をDBに保存する"""
    today = datetime.now().date()
    new_record = models.DailyRecord(
        user_id=mood_data.user_id,
        check_in_date=today,
        color_id=color_id,
        recommend_id=1
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    for answer in mood_data.answers:
        new_answer = models.DailyAnswer(
            check_id=new_record.check_id,
            question_id=answer.question_id,
            answer_choice=answer.answer_choice
        )
        db.add(new_answer)
    db.commit()

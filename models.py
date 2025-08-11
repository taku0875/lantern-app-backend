from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "user" # ER図に合わせて修正
    user_id = Column(Integer, primary_key=True, index=True) # ER図に合わせて修正
    name = Column(String(255))
    email = Column(String(255), unique=True)
    password = Column(String(255))
    prefecture = Column(String(255))
    birthday = Column(Date)
    gender = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Question(Base):
    __tablename__ = "question"
    question_id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer)
    question_text = Column(Text)

class DailyRecord(Base):
    __tablename__ = "daily_record" # ER図に合わせて修正 (旧Diagnose)
    check_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    check_in_date = Column(Date)
    color_id = Column(Integer) # ER図のcolorテーブルへのFKを想定
    recommend_id = Column(Integer) # ER図のrecommendationテーブルへのFKを想定

    # Userテーブルとのリレーション
    user = relationship("User")
    # DailyAnswerテーブルとのリレーション (1対多)
    answers = relationship("DailyAnswer", back_populates="record")

class DailyAnswer(Base):
    __tablename__ = "daily_answer" # ER図に合わせて新規作成
    answer_id = Column(Integer, primary_key=True, index=True)
    check_id = Column(Integer, ForeignKey("daily_record.check_id"))
    question_id = Column(Integer, ForeignKey("question.question_id"))
    answer_choice = Column(Integer)

    # DailyRecordテーブルとのリレーション
    record = relationship("DailyRecord", back_populates="answers")

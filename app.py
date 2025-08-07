# backend/app.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mood_records = []

class MoodData(BaseModel):
    answers: list[int]
    user_id: str

def generate_color_from_answers(answers: list[int]) -> str:
    if not answers:
        return "hsl(240, 10%, 80%)"
        
    total_score = sum(answers)
    avg_score = total_score / len(answers)
    
    hue = 0
    saturation = 0
    lightness = 0

    if avg_score >= 4.5:
        hue = 120
        saturation = 80
        lightness = 70
    elif avg_score >= 3.5:
        hue = 60
        saturation = 70
        lightness = 60
    elif avg_score >= 2.5:
        hue = 240
        saturation = 30
        lightness = 50
    else:
        hue = 0
        saturation = 40
        lightness = 40
    
    return f"hsl({hue}, {saturation}%, {lightness}%)"

@app.post("/mood/save")
async def save_mood(mood_data: MoodData):
    color_code = generate_color_from_answers(mood_data.answers)
    today = datetime.now().strftime("%Y-%m-%d")

    existing_record = next((r for r in mood_records if r["user_id"] == mood_data.user_id and r["date"] == today), None)
    if existing_record:
        existing_record["color_code"] = color_code
    else:
        mood_records.append({
            "user_id": mood_data.user_id,
            "date": today,
            "color_code": color_code,
            "answers": mood_data.answers,
        })
    
    print(f"Saved mood for {mood_data.user_id} on {today} with color {color_code}")
    return {"message": "Mood saved", "color_code": color_code}

@app.get("/mood/week")
async def get_weekly_colors(user_id: str):
    today = datetime.now().date()
    
    weekly_data = sorted([
        record for record in mood_records
        if record["user_id"] == user_id and today - datetime.strptime(record["date"], "%Y-%m-%d").date() <= timedelta(days=7)
    ], key=lambda x: x["date"])

    colors = [record["color_code"] for record in weekly_data]
    return {"colors": colors}
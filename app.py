# backend/app.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta

# おかぴー追加（8/9 9,10行目）
import hashlib
import secrets

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

# おかぴー追加（8/9 90行目以降）
# データモデル定義
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    message: str
    user: dict
    token: str

# ダミーユーザーデータ（実際の開発ではデータベースに保存）
DUMMY_USERS = [
    {
        "id": 1,
        "name": "山田太郎",
        "email": "test@example.com",
        "password": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # "password"をSHA256でハッシュ化
    },
    {
        "id": 2,
        "name": "佐藤花子",
        "email": "user@example.com",
        "password": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",  # "secret123"をSHA256でハッシュ化
    }
]

# シンプルなトークン生成（実際の開発ではJWTを使用推奨）
def generate_token(user_id: int) -> str:
    """ユーザーIDに基づいてトークンを生成"""
    random_str = secrets.token_urlsafe(32)
    timestamp = datetime.now().isoformat()
    return f"{user_id}:{random_str}:{timestamp}"

def hash_password(password: str) -> str:
    """パスワードをSHA256でハッシュ化"""
    return hashlib.sha256(password.encode()).hexdigest()

# デフォルトページ
@app.get("/")
def index():
    return {"message": "FastAPI top page!"}

# ログイン認証
@app.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest):
    """
    ユーザーログイン処理
    """
    try:
        # パスワードをハッシュ化
        hashed_password = hash_password(login_data.password)
        
        # ダミーユーザーデータから認証
        user = None
        for dummy_user in DUMMY_USERS:
            if dummy_user["email"] == login_data.email and dummy_user["password"] == hashed_password:
                user = dummy_user
                break
        
        if not user:
            raise HTTPException(
                status_code=401, 
                detail="メールアドレスまたはパスワードが間違っています"
            )
        
        # トークン生成
        token = generate_token(user["id"])
        
        # レスポンス用のユーザー情報（パスワードは除外）
        user_info = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
        
        return LoginResponse(
            message="ログインに成功しました",
            user=user_info,
            token=token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サーバーエラーが発生しました: {str(e)}")

# 新規会員登録用のデータモデル
class RegisterRequest(BaseModel):
    user_id: str
    password: str
    age: int
    gender: str
    prefecture: str
    phone_number: str
    email: str

class RegisterResponse(BaseModel):
    message: str
    user: dict
    token: str

# 新規会員登録
@app.post("/register", response_model=RegisterResponse)
def register(register_data: RegisterRequest):
    """
    新規会員登録処理（どんな入力でも成功する）
    """
    try:
        # 一意のユーザーIDを生成
        user_id = len(DUMMY_USERS) + 1
        
        # トークン生成
        token = generate_token(user_id)
        
        # 登録されたユーザー情報（パスワードは除外）
        user_info = {
            "id": user_id,
            "user_id": register_data.user_id,
            "name": register_data.user_id,  # 表示名として user_id を使用
            "email": register_data.email,
            "age": register_data.age,
            "gender": register_data.gender,
            "prefecture": register_data.prefecture,
            "phone_number": register_data.phone_number
        }
        
        return RegisterResponse(
            message="会員登録が完了しました",
            user=user_info,
            token=token
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サーバーエラーが発生しました: {str(e)}")

# カラーデータの取得
@app.get("/weekly-colors")
def get_weekly_colors():
    return {"message": "週間カラーデータ取得機能は未実装です"}

# 質問データ取得用のレスポンスモデル
class Question(BaseModel):
    id: int
    categoryId: int
    text: str

class QuestionsResponse(BaseModel):
    questions: list[Question]
    message: str

# ダミー質問データ
DUMMY_QUESTIONS = [
    # 睡眠・身体面（カテゴリID: 1）
    {"id": 1, "categoryId": 1, "text": "夜はぐっすりと眠れていますか？"},
    {"id": 2, "categoryId": 1, "text": "朝、スッキリと目覚めることができますか？"},
    {"id": 3, "categoryId": 1, "text": "体調が良好だと感じますか？"},
    {"id": 4, "categoryId": 1, "text": "日中、適度な活力を感じますか？"},
    {"id": 5, "categoryId": 1, "text": "疲労感なく日常生活を送れていますか？"},
    
    # 感情・気分面（カテゴリID: 2）
    {"id": 6, "categoryId": 2, "text": "心が穏やかで安定していると感じますか？"},
    {"id": 7, "categoryId": 2, "text": "日々の生活に満足感を感じますか？"},
    {"id": 8, "categoryId": 2, "text": "自分の気持ちをうまくコントロールできていますか？"},
    {"id": 9, "categoryId": 2, "text": "ポジティブな気持ちで過ごせる時間が多いですか？"},
    {"id": 10, "categoryId": 2, "text": "笑ったり微笑んだりすることが多いですか？"},
    {"id": 11, "categoryId": 2, "text": "感情の起伏が安定していると感じますか？"},
    
    # 認知・集中面（カテゴリID: 3）
    {"id": 12, "categoryId": 3, "text": "物事に集中して取り組むことができますか？"},
    {"id": 13, "categoryId": 3, "text": "頭がクリアで思考がまとまっていると感じますか？"},
    {"id": 14, "categoryId": 3, "text": "新しいことを学んだり覚えたりするのに意欲的ですか？"},
    {"id": 15, "categoryId": 3, "text": "決断を下すときに迷いが少ないですか？"},
    {"id": 16, "categoryId": 3, "text": "記憶力や理解力に満足していますか？"},
    
    # 社会・人間関係面（カテゴリID: 4）
    {"id": 17, "categoryId": 4, "text": "人との会話を楽しめていますか？"},
    {"id": 18, "categoryId": 4, "text": "家族や友人との時間を心地よく感じますか？"},
    {"id": 19, "categoryId": 4, "text": "困った時に相談できる人がいると感じますか？"},
    {"id": 20, "categoryId": 4, "text": "他の人とのコミュニケーションがスムーズにとれていますか？"},
    {"id": 21, "categoryId": 4, "text": "人とのつながりを大切に感じていますか？"},
    
    # 自己肯定・将来面（カテゴリID: 5）
    {"id": 22, "categoryId": 5, "text": "自分の価値や能力を認めることができますか？"},
    {"id": 23, "categoryId": 5, "text": "将来に対して希望や期待を持てていますか？"},
    {"id": 24, "categoryId": 5, "text": "自分らしく生活できていると感じますか？"},
    {"id": 25, "categoryId": 5, "text": "日々の小さな成功や達成感を味わえていますか？"},
    {"id": 26, "categoryId": 5, "text": "自分に対して前向きな気持ちを持てていますか？"}
]

import random

# 質問の取得
@app.get("/questions", response_model=QuestionsResponse)
def get_questions():
    """
    各カテゴリーから1問ずつランダムに選択して合計5問を返す
    """
    try:
        # カテゴリごとに質問をグループ化
        questions_by_category = {}
        for question in DUMMY_QUESTIONS:
            category_id = question["categoryId"]
            if category_id not in questions_by_category:
                questions_by_category[category_id] = []
            questions_by_category[category_id].append(question)
        
        # 各カテゴリから1問ずつランダム選択
        selected_questions = []
        for category_id in range(1, 6):  # カテゴリ1〜5
            if category_id in questions_by_category:
                category_questions = questions_by_category[category_id]
                random_question = random.choice(category_questions)
                selected_questions.append(random_question)
        
        # Question形式に変換
        questions = [Question(**q) for q in selected_questions]
        
        return QuestionsResponse(
            questions=questions,
            message="質問を正常に取得しました"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"質問取得エラー: {str(e)}")

# 回答結果の取得
@app.get("/daily-result")
def get_daily_result(day: str = Query(..., description="曜日（月、火、水、木、金、土、日）")):
    """
    指定された曜日の回答結果を取得
    """
    # ダミーデータ（5問の質問と回答）
    dummy_results = {
        "月": { 
            "questions": [
                {"question": "今日の気分はどうでしたか？", "answer": "とても良かった"},
                {"question": "ストレスを感じる場面はありましたか？", "answer": "特になし"},
                {"question": "睡眠の質はどうでしたか？", "answer": "よく眠れた"},
                {"question": "人との関わりはどうでしたか？", "answer": "楽しく過ごせた"},
                {"question": "今日一番印象に残ったことは？", "answer": "新しいプロジェクトが始まったこと"}
            ],
            "timestamp": "2024/08/08 18:30"
        },
        "火": { 
            "questions": [
                {"question": "今日の気分はどうでしたか？", "answer": "普通"},
                {"question": "ストレスを感じる場面はありましたか？", "answer": "会議で少し緊張した"},
                {"question": "睡眠の質はどうでしたか？", "answer": "まあまあ"},
                {"question": "人との関わりはどうでしたか？", "answer": "同僚と良い議論ができた"},
                {"question": "今日一番印象に残ったことは？", "answer": "新しいアイデアが浮かんだ"}
            ],
            "timestamp": "2024/08/09 19:15"
        },
        "水": { 
            "questions": [
                {"question": "今日の気分はどうでしたか？", "answer": "良い"},
                {"question": "ストレスを感じる場面はありましたか？", "answer": "締切に追われて少し焦った"},
                {"question": "睡眠の質はどうでしたか？", "answer": "少し浅かった"},
                {"question": "人との関わりはどうでしたか？", "answer": "チームワークが良かった"},
                {"question": "今日一番印象に残ったことは？", "answer": "難しい問題を解決できた"}
            ],
            "timestamp": "2024/08/10 17:45"
        },
        "木": { 
            "questions": [
                {"question": "今日の気分はどうでしたか？", "answer": "とても良い"},
                {"question": "ストレスを感じる場面はありましたか？", "answer": "特になし"},
                {"question": "睡眠の質はどうでしたか？", "answer": "ぐっすり眠れた"},
                {"question": "人との関わりはどうでしたか？", "answer": "上司に褒められた"},
                {"question": "今日一番印象に残ったことは？", "answer": "プロジェクトが大きく進展した"}
            ],
            "timestamp": "2024/08/11 18:00"
        },
        "金": None,
        "土": None,
        "日": None,
    }
    
    # 指定された曜日のデータを返す
    if day in dummy_results:
        return dummy_results[day]
    else:
        raise HTTPException(status_code=400, detail="不正な曜日が指定されました")

# 提案行動の取得
@app.post("/suggested-actions")
def get_suggested_actions():
    return {"message": "提案行動取得機能は未実装です"}
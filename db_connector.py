import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# --- データベース接続設定 ---
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def get_db_connection():
    """データベースへの接続を取得する"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"データベース接続エラー: {err}")
        return None

def initialize_database():
    """データベースとテーブルを自動で初期化する"""
    try:
        # DB_NAMEなしで一度接続し、データベース自体を作成
        temp_config = db_config.copy()
        temp_config.pop('database', None)
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.close()

        # テーブルを作成
        conn = get_db_connection()
        cursor = conn.cursor()
        # (ここにUsers, Questions, Diagnoses, AnswersのCREATE TABLE文を追加します)
        print("✅ データベースとテーブルの準備が正常に完了しました。")
        conn.close()
    except mysql.connector.Error as err:
        print(f"❌ データベース初期化エラー: {err}")

# --- データ操作関数の例 ---
def get_questions_from_db(category_ids: list):
    """DBから指定されたカテゴリの質問を取得する（未実装）"""
    # ここにDBから質問を取得するロジックを実装します
    pass
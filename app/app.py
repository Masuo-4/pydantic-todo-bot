from flask import Flask, request, render_template, redirect
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from models import TaskItem
from db import init_db, save_task, get_all_tasks, delete_task
from datetime import date
import dateparser
import asyncio
import os
import traceback
import re
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# Flaskアプリ初期化
app = Flask(__name__, template_folder="templates")

# Geminiモデル・エージェント
model = GeminiModel("gemini-2.0-flash")
agent = Agent(model=model, output_type=TaskItem)

# DB初期化
init_db()

# 🔗 URLをHTMLリンクに変換する関数
def convert_links(text: str) -> str:
    url_pattern = r'(https?://[^\s]+)'
    return re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)

# 非同期実行ハンドリング
def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    else:
        return asyncio.ensure_future(coro)

@app.route("/", methods=["GET"])
def index():
    sort = request.args.get("sort", "due")  # デフォルト: 締切順
    tasks = get_all_tasks(sort=sort)
    return render_template("index.html", tasks=tasks, sort=sort)

@app.route("/add", methods=["POST"])
def add_task_web():
    try:
        text = request.form.get("text", "")
        today = date.today().strftime('%Y-%m-%d (%a)')
        print("📥 入力:", text)

        prompt = f"""
今日は {today} です。次の文章からタスクを抽出してください。
もし期限が記載されていれば、日付だけでなく「何時までか」などの時刻も含めてください（例: 2025-08-02 18:00）。
出力は ISO8601形式の文字列でお願いします。また、期限は現在以降の時間しか出力しないでください。また、補足情報はなるべく漏らさず抽出してください。
文章: {text}
"""

        result = run_async(agent.run(prompt))
        if hasattr(result, "result"):
            result = asyncio.get_event_loop().run_until_complete(result)

        print("🧠 Gemini抽出結果:", result.output)

        if result.output.due_date:
            parsed = dateparser.parse(result.output.due_date, settings={"PREFER_DATES_FROM": "future"})
            due_date = parsed.strftime('%Y-%m-%d %H:%M') if parsed else None
        else:
            due_date = None

        # 🔗 リンク変換して保存
        details_with_links = convert_links(result.output.details)
        save_task(result.output.title, due_date, details_with_links)

        return render_template("result.html", task={
            "title": result.output.title,
            "due_date": due_date,
            "details": details_with_links,
        })

    except Exception as e:
        print("🔥 エラー:", e)
        traceback.print_exc()
        return f"<p>エラー: {e}</p><a href='/'>戻る</a>"

@app.route("/done/<int:task_id>", methods=["POST"])
def done(task_id):
    try:
        delete_task(task_id)
        return redirect("/")
    except Exception as e:
        print("🔥 完了処理エラー:", e)
        traceback.print_exc()
        return f"<p>エラー: {e}</p><a href='/'>戻る</a>"

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)

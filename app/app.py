from flask import Flask, request, render_template
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from models import TaskItem
from db import init_db, save_task, get_all_tasks
from datetime import date
import dateparser
import asyncio
import os
import traceback
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Flask アプリ初期化
app = Flask(__name__, template_folder="templates")

# Gemini エージェント初期化
model = GeminiModel("gemini-2.0-flash")
agent = Agent(model=model, output_type=TaskItem)

# DB 初期化
init_db()

# ⚠️ asyncio.run()ではなく、asyncio loop の再利用を明示的に行う関数
def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    else:
        return asyncio.ensure_future(coro)  # すでに走ってるなら ensure_future

# 📄 タスク一覧ページ
@app.route("/", methods=["GET"])
def index():
    tasks = get_all_tasks()
    return render_template("index.html", tasks=tasks)

# 📝 タスク追加処理
@app.route("/add", methods=["POST"])
def add_task_web():
    try:
        text = request.form.get("text", "")
        today = date.today().strftime('%Y-%m-%d (%a)')

        print("📥 入力:", text)

        prompt = f"""
今日は {today} です。次の文章からタスクを抽出してください。期限は基本平日になります。： {text}
"""

        # 🔁 安定した非同期実行
        result = run_async(agent.run(prompt))
        if hasattr(result, "result"):  # ensure_future()のとき
            result = asyncio.get_event_loop().run_until_complete(result)

        print("🧠 Gemini抽出結果:", result.output)

        if result.output.due_date:
            parsed = dateparser.parse(
                result.output.due_date, settings={"PREFER_DATES_FROM": "future"}
            )
            due_date = parsed.date().isoformat() if parsed else None
        else:
            due_date = None

        save_task(result.output.title, due_date, result.output.details)

        return render_template("result.html", task={
            "title": result.output.title,
            "due_date": due_date,
            "details": result.output.details,
        })

    except Exception as e:
        print("🔥 エラー:", e)
        traceback.print_exc()
        return f"<p>エラー: {e}</p><a href='/'>戻る</a>"
# 🚀 アプリ起動
if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
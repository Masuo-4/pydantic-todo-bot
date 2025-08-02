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
import markdown as md
import bleach
import re
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

app = Flask(__name__, template_folder="templates")

model = GeminiModel("gemini-2.0-flash")
agent = Agent(model=model, output_type=TaskItem)

init_db()

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    else:
        return asyncio.ensure_future(coro)

# Markdown→HTML（安全化）
def render_markdown(text: str) -> str:
    html = md.markdown(text)
    return bleach.clean(
        html,
        tags=["p", "ul", "ol", "li", "strong", "em", "a", "code", "pre", "br"],
        attributes={"a": ["href", "title", "target"]},
        protocols=["http", "https"]
    )

@app.route("/", methods=["GET"])
def index():
    sort = request.args.get("sort", "due")
    tasks = get_all_tasks(sort=sort)
    return render_template("index.html", tasks=tasks, sort=sort)

@app.route("/add", methods=["POST"])
def add_task_web():
    try:
        text = request.form.get("text", "")
        today = date.today().strftime('%Y-%m-%d (%a)')

        prompt = f"""
今日は {today} です。次の文章からタスクを抽出してください。
タスクの説明（details）はMarkdown形式で漏れなく見やすく整理して書いてください。
出力は ISO8601形式の文字列でお願いします。期限は現在以降の時間にしてください。
文章: {text}
"""

        result = run_async(agent.run(prompt))
        if hasattr(result, "result"):
            result = asyncio.get_event_loop().run_until_complete(result)

        if result.output.due_date:
            parsed = dateparser.parse(result.output.due_date, settings={"PREFER_DATES_FROM": "future"})
            due_date = parsed.strftime('%Y-%m-%d %H:%M') if parsed else None
        else:
            due_date = None

        details_with_md = render_markdown(result.output.details)
        save_task(result.output.title, due_date, details_with_md)
        print(details_with_md)

        return render_template("result.html", task={
            "title": result.output.title,
            "due_date": due_date,
            "details": details_with_md,
        })

    except Exception as e:
        traceback.print_exc()
        return f"<p>エラー: {e}</p><a href='/'>戻る</a>"

@app.route("/done/<int:task_id>", methods=["POST"])
def done(task_id):
    try:
        delete_task(task_id)
        return redirect("/")
    except Exception as e:
        traceback.print_exc()
        return f"<p>エラー: {e}</p><a href='/'>戻る</a>"

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)

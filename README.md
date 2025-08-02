# pydantic ToDo Bot Updated (Docker + uv)

## 概要

自然言語で入力されたタスクを、Google Gemini API（google-generativeai）で構造化し、
SQLite に保存して ToDo 一覧として表示できる Webアプリです。

## セットアップ手順

```bash
git clone <REPO_URL>
cd pydantic-todo-bot-updated

export GOOGLE_API_KEY=your-gemini-api-key-here

docker compose up --build
```

ブラウザで http://localhost:5000 にアクセスしてください。

## API および UI

- `/` (GET): タスク一覧と追加フォーム
- `/add` (POST): 自然言語タスクを追加

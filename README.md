# ✅ Pydantic ToDo Bot

自然言語で記述したタスク内容から、構造化されたToDo情報（タイトル、期限、詳細）を抽出して管理するWebアプリです。

Gemini 2.5 Flash と `pydantic-ai` を使用し、曖昧な日本語から構造化データを自動抽出します。

---

## 🚀 使用技術

- Python 3.11
- Flask
- SQLite
- [pydantic-ai](https://github.com/pydantic/pydantic-ai)
- Gemini 2.5 Flash（Google Generative AI）
- uv（Python依存管理＆実行）

---

## 📂 ディレクトリ構成

```
.
├── app/                  # Flaskアプリ本体
│   ├── app.py            # メインのFlaskアプリ
│   ├── db.py             # SQLite操作ロジック
│   ├── models.py         # Pydanticモデル定義
│   └── templates/        # HTMLテンプレート
│       ├── index.html
│       └── result.html
├── db/                   # SQLite DBの永続化ディレクトリ
├── .env                  # 環境変数（GOOGLE_API_KEY）
├── requirements.in       # 依存パッケージ定義
├── uv.lock               # uvロックファイル
├── pyproject.toml        # uvによるメタ情報
└── README.md             # このファイル
```

---

## ⚙️ セットアップ手順（Docker未使用）

### 1. uvのインストール

```bash
curl -Ls https://astral.sh/uv/install.sh | bash
```

インストール後、以下で依存関係をインストールします：

```bash
uv sync
```

---

### 2. APIキーの設定

`.env` ファイルを作成し、以下のように記述：

```
GOOGLE_API_KEY=your-google-api-key-here
```

---

### 3. アプリ起動

```bash
uv run app/app.py
```

ブラウザで [http://localhost:5000](http://localhost:5000) にアクセス。

---

## ✨ 機能概要

- 自然言語から「タイトル」「期限」「詳細」を自動抽出
- 抽出結果はSQLite DBに保存
- 保存済みタスクは一覧で表示される

---

## 📝 入力例

```
金曜日までに出張の準備を終える。内容は資料印刷と荷造り。
```

→ 自動抽出された構造：

```json
{
  "title": "出張の準備",
  "due_date": "2025-08-09",
  "details": "資料印刷と荷造り"
}
```

---

## 📌 注意事項

- Google Gemini APIキーは[こちらから取得](https://makersuite.google.com/app/apikey)してください。
- SQLiteファイルは `db/tasks.db` に永続化されます。

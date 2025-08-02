FROM python:3.11

# uvをインストールするために必要なパッケージを先に入れる（curl, unzipなど）
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# uvのインストール（公式推奨スクリプト）
RUN curl -Ls https://astral.sh/uv/install.sh | bash

# 環境変数PATHを明示的に通す（/root/.cargo/bin にuvが入る）
ENV PATH="/root/.cargo/bin:${PATH}"

# 作業ディレクトリ設定
WORKDIR /app

# uvのプロジェクト初期化（pyproject.tomlなど）
RUN uv init .

# requirements.in / uv.lock をコピー
COPY requirements.in .
COPY uv.lock .

# 依存パッケージのインストール（--systemを付けない新方式）
RUN uv sync

# アプリケーションコードをコピー
COPY app/ ./app

# サーバー起動コマンド（FastAPIなら uvicorn など）
CMD ["uv", "run", "app/app.py", "--host", "0.0.0.0", "--port", "5000"]

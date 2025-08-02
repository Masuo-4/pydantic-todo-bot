from pydantic import BaseModel, Field

class TaskItem(BaseModel):
    title: str = Field(..., description="タスクのタイトル")
    due_date: str = Field(..., description="期限。ISO8601形式（例: 2025-08-02 18:00）")
    details: str = Field(..., description="タスクの説明や補足(markdown)")

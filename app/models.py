from pydantic import BaseModel, Field


class TaskItem(BaseModel):
    title: str = Field(..., description="タスクのタイトル")
    due_date: str = Field(..., description="期限。ISO8601形式の文字列")
    details: str = Field(..., description="タスクの説明や補足")

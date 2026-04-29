from pydantic import BaseModel, Field

from typing import Optional
from datetime import timezone,  datetime

#  Base Model
class TasksBase(BaseModel):
    title: str = Field(min_length= 3, max_length = 20, pattern=r"^[A-Za-z0-9 ]+$", description='title for the task')
    description: Optional[str] = Field(min_length= 3, max_length = 40, default=None)
    completed: bool = Field(default=False)


class TasksCreate(TasksBase):
    description: Optional[str] = Field(min_length=3, max_length=100, default=None)



class  TasksUpdate(BaseModel):
    title: Optional[str] =None
    description: Optional[str] =None
    completed: Optional[bool] =None

# db schemas
class Tasks(TasksBase):
    id: int = Field(default=None, primary_key=True, autoincrement=True, description='title for the task')
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TasksRead(TasksBase):
    id: int
    created_at: datetime
    updated_at: datetime


class TasksDelete(BaseModel):
    pass
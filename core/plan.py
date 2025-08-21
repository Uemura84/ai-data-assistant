# core/plan.py
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

Action = Literal["aggregate", "count_distinct", "filter", "top_n", "message"]

class Plan(BaseModel):
    action: Action
    column: Optional[str] = None
    agg: Optional[Literal["mean","sum","min","max","median","count"]] = None
    group_by: Optional[List[str]] = Field(default=None)
    predicates: Optional[str] = None
    by: Optional[str] = None
    n: Optional[int] = 5
    ascending: Optional[bool] = False
    text: Optional[str] = None

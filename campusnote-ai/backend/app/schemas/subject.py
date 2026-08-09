from pydantic import BaseModel
from typing import Optional, List


class TopicOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class UnitCreate(BaseModel):
    name: str
    order_index: int = 0


class UnitOut(BaseModel):
    id: str
    name: str
    order_index: int
    topics: List[TopicOut] = []

    class Config:
        from_attributes = True


class SubjectCreate(BaseModel):
    name: str
    code: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[str] = None
    units: Optional[List[str]] = None  # simple list of unit names to create


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[str] = None


class SubjectOut(BaseModel):
    id: str
    name: str
    code: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[str] = None
    units: List[UnitOut] = []

    class Config:
        from_attributes = True

from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, Field, StringConstraints, ConfigDict
from pydantic import BaseModel, EmailStr, ConfigDict, StringConstraints

NameStr = Annotated[str, StringConstraints(min_length=1, max_length =100)]
YearStarted = Annotated[int, Ge(1900), Le(2100)]
BookTitleStr = Annotated[str, StringConstraints(min_length=1, max_length = 255)]
BookPages = Annotated[int, Ge(1), Le(10000)]

#Authors
class AuthorCreate(BaseModel):
    name: NameStr
    email: EmailStr
    year_started: YearStarted

class AuthorPatch(BaseModel):
    name: Optional[NameStr] = None
    email: Optional[EmailStr] = None
    year_started: Optional[YearStarted] = None

class AuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: NameStr
    email: EmailStr
    year_started: YearStarted

#Books 
class BookCreate(BaseModel):
    title: BookTitleStr
    pages: BookPages
    author_id: int

class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: BookTitleStr
    pages: BookPages
    author_id: int

# app/main.py
from typing import Optional

from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, response_model
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import engine, SessionLocal
from app.models import Base, AuthorDB, BookDB
from app.schemas import AuthorCreate, AuthorPatch, AuthorRead, BookCreate, BookRead
#from app.schemas import 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (dev/exam). Prefer Alembic in production.
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

def commit_or_rollback(db: Session, error_message:str):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=error_message)

# ---- Health ----
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("api/author", response_model=AuthorRead, status_code=201)
def create_author(payload: AuthorCreate, db:Session = Depends(get_db)):
    author = AuthorDB(**payload.model_dump())
    db.add(author)
    try:
        db.commit()
        db.refresh(author)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Author already esists")
    return author

@app.get("api/author", response_model = list[AuthorRead], status_code=200)
def get_authors(db: Session = Depends(get_db)):
    stmt=select(AuthorDB).order_by(AuthorDB.id)
    result = db.execute(stmt)
    authors = result.scalars().all()
    return authors

@app.get("/api/authors/{author_id}", response_model=AuthorRead, status_code=200)
def get_author(author_id: int, db:Session = Depends(get_db)):
    author = db.get(AuthorDB, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="not found")
    return author

@app.put("api/author/{author_id}", response_model= AuthorRead, status_code= status.HTTP_202_ACCEPTED)
def update_author(author_id: int, payload: AuthorCreate, db:Session=Depends(get_db)):
    author = db.get(AuthorDB, author_id)
    if not author:
        raise HTTPException(status_code = 404, detail="User not found")
    
    for key, value in payload.model_dump().items():
        setattr(author, key, value)

    commit_or_rollback(db, "failed to update author")
    db.refresh(author)
    return author

@app.patch("api/author/{author_id}", response_model = AuthorRead, status_code= 200)
def patch_author(author_id: int, payload: AuthorPatch, db:Session=Depends(get_db)):
    author=db.get(AuthorDB, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(author, key, value)
    
    commit_or_rollback(db, "Failed to update author")
    db.refresh(author)
    return author

@app.delete("api/author/{author_id}", status_code=204)
def delete_author(author_id: int, db: Session=Depends(get_db)):
    author = db.get(AuthorDB, author_id)
    if not author: 
        raise HTTPException(status_code=409, detail="Author not found")
    db.delete(author)
    db.commit()
    return response_model(status_code = status.HTTP_204_NO_CONTENT)

#Books
@app.post("api/books", response_model=BookRead, status_code=201)
def add_book(book: BookCreate, db:Session = Depends(get_db))
    book = db.get(AuthorDB, book.author_id)
    if not author: 
        raise HTTPException(status_code=404)
    
    Book = BookDB(
        title = book.title
        pages = book.pages
        author_id = author_id
    )

    db.add(Book)
    commit_or_rollback(db, "Book add failed")
    db.refresh(Book)
    return Book

# @app.get("/api/book/{author_id}", response_model=AuthorRead, status_code=200)
# def get_author(author_id: int, db:Session = Depends(get_db)):
#     author = db.get(AuthorDB, author_id)
#     if not author:
#         raise HTTPException(status_code=404, detail="not found")
#     return author
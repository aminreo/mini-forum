import sqlite3
from contextlib import closing
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from pwdlib import  PasswordHash


app = FastAPI()
passwords = PasswordHash.recommended()

with closing (sqlite3.connect("forum.db")) as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
    """)
    db.commit()

def get_db():
    db = sqlite3.connect("forum.db")
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.close()

class Registration (BaseModel):
    username: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[a-z0_9_]+$"
    )
    password: str = Field(min_length=15, max_length=128)

class Login(BaseModel):
    username: str = Field (min_length=1, max_length=30)
    password: str = Field (min_length=1, max_length=128)

@app.post("/register",status_code=201)
def register(data: Registration, db=Depends(get_db)):
    hashed_password = passwords.hash(data.password)
    try:
        cursor = db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?,?)",
            (data.username,hashed_password)
        )
        db.commit()
    except:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username already taken",
        )
    return {"id":cursor.lastrowid, "username":data.username}

DUMMY_HASH = passwords.hash("not-a-real-account-password")

@app.post("/login")
def login(data:Login,db=Depends(get_db) ):
    user= db.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (data.username,),
    ).fetchone()
    stored_hash = user ["password_hash"] if user else DUMMY_HASH
    valid_password = passwords.verify(data.password,stored_hash)

    if user is None or not valid_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )
    return {
        "message": "Credentials verified",
        "user_id": user["id"],
    }
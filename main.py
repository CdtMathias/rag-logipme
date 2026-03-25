from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field
from agent import chat
from auth import hash_password, verify_password, create_token, verify_token
from fastapi.security import OAuth2PasswordRequestForm
from database import get_user, create_user
from rag import index_document
import tempfile
import os

app = FastAPI()

@app.get("/")
def home():
    return {"Message": "LogiPME"}

@app.post("/index")
def index_endpoint(file: UploadFile = File(...), payload = Depends(verify_token)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    index_document(file.filename, tmp_path)
    os.unlink(tmp_path)
    return {"message": f"{file.filename} indexé avec succès."}

class ChatSchema(BaseModel):
    message: str = Field(min_length=1)

@app.post("/chat")
def chat_endpoint(body: ChatSchema, payload = Depends(verify_token)):
    user_id = int(payload["sub"])
    response = chat(body.message, user_id)
    return {"response": response}

    # USER #

class UserSchema(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    password: str = Field(min_length=5, max_length=20)

@app.post("/register")
def register(user: UserSchema):
    try:
        hashed_password = hash_password(user.password)
        create_user(user.username, hashed_password)
        return {"message": "Account created"}
    except Exception:
        raise HTTPException(status_code=409, detail="Username already exists")

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_data = get_user(form_data.username)
    if not user_data:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not verify_password(form_data.password, user_data[2]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    user_id = user_data[0]
    return {"access_token": create_token({"sub": str(user_id)}), "token_type": "bearer"}

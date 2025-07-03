from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

# In-memory item list
users = []


class User(BaseModel):
  username: str
  email: str
  password: str

@app.post("/register")
def register_user(user: User):
  users.append(user)
  return "Successfully added user to database"

@app.get("/users")
def get_users():
  return users

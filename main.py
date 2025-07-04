# from fastapi import FastAPI
# from pydantic import BaseModel
# from fastapi import HTTPException
# from fastapi.responses import JSONResponse
import pandas as pd
import os

# app = FastAPI()

# In-memory item list
users = []

current_dir = os.getcwd()
file_path = f"{current_dir}/imdb-movies-dataset.csv"
print(file_path)

df = pd.read_csv("C:\\Users\\danus\\OneDrive\\VS_code_projects\\movie_explorer\\imdb-movies-dataset.csv", encoding="utf-8")
print(df.head(1))
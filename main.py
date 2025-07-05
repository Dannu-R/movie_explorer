from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, root_validator
from typing import Optional
import os
import pandas as pd
import math


app = FastAPI()

class Movie(BaseModel):
  Poster: Optional[str]
  Title: Optional[str]
  Year: Optional[int]
  Certificate: Optional[str]
  Duration: Optional[int]
  Genre: Optional[str]
  Rating: Optional[float]
  Metascore: Optional[int]
  Director: Optional[str]
  Cast: Optional[str]
  Votes: Optional[str]
  Description: Optional[str]
  Review_Count: Optional[str]
  Review_Title: Optional[str]
  Review: Optional[str]

  @root_validator(pre=True)
  def replace_nan_with_none(cls, values):
    for key in values:
    #   print(f"{values[key]}")
      if isinstance(values[key], float) and math.isnan(values[key]):
          values[key] = None
    return values


movies: list[Movie] = []
try:
  current_dir = os.getcwd()

  raw_df = pd.read_csv(f"{current_dir}/imdb-movies-dataset.csv", encoding="utf-8")
  movie_df = raw_df.rename(columns={
      "Duration (min)": "Duration",
      "Review Count": "Review_Count",
      "Review Title": "Review_Title"
  })

  for n in range(0, len(movie_df)-1):
    if n < 15:
      movies.append(Movie(**movie_df.loc[n].to_dict()))
except Exception as e:
  print("🚨 Error while loading movies:", e)
  movies = []



@app.get("/movies", response_model=list[Movie])
def get_movies(limit):
  limit = int(limit)
  if limit >= 10 or limit <= 0:
     raise HTTPException(status_code=404, detail="list index out of range")
  return movies[0: limit]

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, root_validator, validator
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
    # print(f"⚠️{values}")
    for key in values:
      if isinstance(values[key], float) and math.isnan(values[key]):
          values[key] = None
    return values
  @validator('Genre')
  def get_genre_list(cls, value):
    if value != None:
      return value.split(', ')
  
  @validator("Cast")
  def get_cast_list(cls, value):
    if value != None:
      return value.split(', ')


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
    movies.append(Movie(**movie_df.loc[n].to_dict()))
  print(type(movies[0]))
except Exception as e:
  print("🚨 Error while loading movies:", e)



@app.get("/movie/search/{title}")
def get_movie_by_title(title: str):
  idx = movie_df.index[movie_df["Title"] == title]  # Index object
  try:
    idx_value = idx[0]
    return movies[idx_value]
  except:
    raise HTTPException(status_code=404, detail="Movie not found")

@app.get("/movie/top/{genre}", response_model=list[Movie])
def get_best_movies(genre = str):
  genre_movies = []
  genre_df = movie_df[movie_df['Genre'] == genre]
  for n in genre_df.index:
    if n<3
    genre_movies.append(Movie(**genre_df.loc[n].to_dict()))
    print(f"{genre_df.loc[n].to_dict()}")
  return genre_movies[0] 

@app.get("/movies", response_model=list[Movie])
def get_movies(
  limit: int,  # still required
  year: Optional[int] = None,
  certificate: Optional[str] = None,
  duration: Optional[int] = None,
  genre: Optional[str] = None,
  rating: Optional[float] = None,
  metascore: Optional[int] = None,
  director: Optional[str] = None,
  cast: Optional[str] = None
):
  filtered_movies: list[Movie] = []
  limit = int(limit)
  if limit < 1:
   raise HTTPException(status_code=404, detail="list index out of range")
  filtered_df = movie_df

  if year is not None:
    filtered_df = filtered_df[filtered_df["Year"] == year]

  if certificate is not None:
    filtered_df = filtered_df[filtered_df["Certificate"].str.lower() == certificate.lower()]

  if duration is not None:
    filtered_df = filtered_df[filtered_df["Duration"] >= duration]

  if genre is not None:
    if genre is not None:
      genres = genre.lower().split("-")
      mask = movie_df["Genre"].str.lower().fillna("").apply(lambda g: any(gen in g for gen in genres))
      filtered_df = filtered_df[mask]

  if rating is not None:
    filtered_df = filtered_df[filtered_df["Rating"] >= rating]

  if metascore is not None:
    filtered_df = filtered_df[filtered_df["Metascore"] >= metascore]

  if director is not None:
    filtered_df = filtered_df[filtered_df["Director"].str.contains(director, case=False, na=False)]
  
  if cast is not None:
    cast_members = cast.lower().split("-")
    mask = movie_df["Cast"].str.lower().fillna("").apply(lambda c: any(actor in c for actor in cast_members))
    filtered_df = filtered_df[mask]

    
  counter = 0
  for n in filtered_df.index:
    if counter < limit:
      filtered_movies.append(Movie(**filtered_df.loc[n].to_dict()))
    counter += 1
  return filtered_movies
    


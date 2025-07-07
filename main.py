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
    for key in values:
      val = values[key]
      if isinstance(val, float) and math.isnan(val):
          values[key] = None
    return values
  
  @validator('Votes')
  def catch_votes(cls, value):
    if "," in str(value):
      value = int(str(value).replace(",", ""))
    return value
  
  @validator('Genre')
  def get_genre_list(cls, value):
    if value != None:
      return value.split(', ')
  
  @validator("Cast")
  def get_cast_list(cls, value):
    if value != None:
      return value.split(', ')

  @validator('Rating', always=True, pre=False)
  def change_rating(cls, value):
    if value == None:
      value = 0
    return value


class Stats(BaseModel):
  average_ratings: list[float]
  movie_count: int

  @validator('average_ratings')
  def get_average(cls, value: list[float]):
    return round((sum(value) / len(value)), 2)
  
  
movies: list[Movie] = []
movie_df = pd.DataFrame()

@app.on_event("startup")
async def load_movies():
  global movies, movie_df
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
  except Exception as e:
    print("🚨 Error while loading movies:", e)



@app.get("/movie/search/{title}", response_model=Movie)
def get_movie_by_title(title: str):
  global movies
  for i in range(0, len(movies)):
    if movies[i].Title == title:
      return movies[i]
  raise HTTPException(status_code=404, detail=f"{len(movies)}")

@app.get("/movie/top/{genre}", response_model=list[Movie])
def get_best_movies(genre: str, limit: int):
  genre_movies = []
  genre_df = movie_df[movie_df['Genre'] == genre]
  for n in genre_df.index:
    genre_movies.append(Movie(**genre_df.loc[n].to_dict()))
  genre_movies = sorted(genre_movies, key=lambda x: x.Rating, reverse=True) 
  return genre_movies[0: limit] 

@app.get("/movie/stats/{genre}", response_model=Stats)
def get_movie_stats(genre: str):
  ratings = []
  try:
    genre_df = movie_df[movie_df['Genre'] == genre]
  except:
    raise HTTPException(status_code=404, detail="Genre not in database")
  genre_movies = [Movie(**genre_df.loc[n].to_dict()) for n in genre_df.index]
  for movie in genre_movies:
    if movie.Rating != None:
      ratings.append(movie.Rating) 
  parameters = {"average_ratings": ratings, "movie_count": len(ratings)}
  return Stats(**parameters)

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
    

@app.post("/movies", response_model=Movie)
def add_movie(
  Poster: Optional[str] = None,
  Title: Optional[str] = None,
  Year: Optional[int] = None,
  Certificate: Optional[str] = None,
  Duration: Optional[int] = None,
  Genre: Optional[str] = None,
  Rating: Optional[float] = None,
  Metascore: Optional[int] = None,
  Director: Optional[str] = None,
  Cast: Optional[str] = None,
  Votes: Optional[int] = None,
  Description: Optional[str] = None,
  Review_Count: Optional[str] = None,
  Review_Title: Optional[str] = None,
  Review: Optional[str] = None
):
  movies.append(Movie(**locals()))
  return movies[-1]
  
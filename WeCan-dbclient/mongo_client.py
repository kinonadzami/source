from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient


config = dotenv_values(".env")

app = FastAPI()
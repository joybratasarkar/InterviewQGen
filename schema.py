from pydantic import BaseModel, Field
from typing import List
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Define the schema for individual questions using Pydantic
class QuestionSchema(BaseModel):
    question: str = Field(..., min_length=1, description="The interview question.")
    difficulty: str = Field(
        ..., 
        pattern='^(Easy|Medium|Hard)$',  # Correct usage of pattern instead of regex
        description="Difficulty level of the question."
    )

# Define the schema for the list of questions including the projectId
class QuestionListSchema(BaseModel):
    projectId: str = Field(..., description="The ID of the project associated with these questions.")
    questions: List[QuestionSchema]

# MongoDB connection setup
mongo_uri = os.getenv("MONGODB_URI")
print('mongo_uri', mongo_uri)
client = MongoClient(mongo_uri)
db = client.get_database('ai-interview-questions')  # Use the correct database name
questions_collection = db.get_collection("questions")  # Collection to save questions

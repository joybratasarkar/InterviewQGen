from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import load_summarize_chain
from langchain.schema import Document
from transformers import BartTokenizer, BartForConditionalGeneration
import torch
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
import openai
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pymongo import MongoClient
from typing import List
from pymongo import MongoClient
from schema import QuestionListSchema, questions_collection  # Importing schema and MongoDB setup

# Load environment variables from the .env file
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize BART model and tokenizer with the lighter version
tokenizer = BartTokenizer.from_pretrained('facebook/bart-base')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-base')

# Initialize OpenAI LLM
llm = OpenAI()

# Load the summarization chain from LangChain
summarize_chain = load_summarize_chain(llm, chain_type="map_reduce")

# Define the prompt template for generating interview questions
question_prompt_template = """
You are a professional interviewer tasked with creating a set of interview questions for a specific job role. Based on the summarized job description provided below, generate a list of exactly 5 interview questions for each of the following categories: Easy, Medium, and Hard. Each question should be relevant to the role and designed to effectively assess the candidate's skills, experience, and cultural fit for the position.

Job Description Summary:
{job_description_summary}

Questions:
- Easy (5 questions):
- Medium (5 questions):
- Hard (5 questions):
"""

# Create a PromptTemplate instance for generating interview questions
question_prompt = PromptTemplate(template=question_prompt_template, input_variables=["job_description_summary"])

class JobDescription(BaseModel):
    description: str

# Model to handle saving questions
class QuestionSelection(BaseModel):
    questions: List[str]

# Set up MongoDB client
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client.get_database("interview_db")  # Replace 'interview_db' with your database name
questions_collection = db.get_collection("questions")  # Replace 'questions' with your collection name

# Create a thread pool executor for parallel processing
executor = ThreadPoolExecutor(max_workers=16)

@lru_cache(maxsize=100)
def get_cached_summary(job_description):
    return asyncio.run(summarize_job_description(job_description))

async def summarize_job_description(job_description):
    chunk_size = 1024
    chunks = [job_description[i:i + chunk_size] for i in range(0, len(job_description), chunk_size)]
    
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(executor, process_chunk, chunk) for chunk in chunks]
    summaries = await asyncio.gather(*tasks)
    
    full_summary = " ".join(summaries)
    return full_summary

def process_chunk(chunk):
    document = Document(page_content=chunk)
    summary = summarize_chain.run([document])
    return summary

async def generate_interview_questions(job_description_summary):
    prompt = question_prompt.format(job_description_summary=job_description_summary)
    questions = llm(prompt)
    return questions.strip()

@app.post("/generate")
async def generate(job_description: JobDescription):
    try:
        summary = await summarize_job_description(job_description.description)
        logger.info('Job Description Summary: %s', summary)
        questions = await generate_interview_questions(summary)
        logger.info('Generated Questions: %s', questions)
        return {"questions": questions}
    except Exception as e:
        logger.error('Error occurred: %s', str(e))
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/save")
async def save_questions(question_list: QuestionListSchema):
    """
    Endpoint to save a list of questions to the MongoDB database, along with a projectId.
    """
    try:
        # Log the incoming request data
        logger.info("Incoming request data: %s", question_list)

        # Convert the incoming data to a dictionary
        validated_data = question_list.model_dump()
        project_id = validated_data['projectId']  # Extract projectId
        print('project_id', project_id)

        # Prepare the document to be inserted into MongoDB
        document = {
            'projectId': project_id,
            'questions': [
                {'question': q['question'], 'difficulty': q['difficulty']}
                for q in validated_data['questions']
            ]
        }

        # Log the document structure
        print('Document to be inserted:', document)

        # Insert the document into the MongoDB collection
        result = questions_collection.insert_one(document)
        
        logger.info('Questions saved successfully')
        return {"message": "Questions saved successfully", "inserted_id": str(result.inserted_id)}
    
    except ValidationError as e:
        logger.error('Validation error: %s', e.errors())
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        logger.error('Error occurred while saving questions: %s', str(e))
        raise HTTPException(status_code=500, detail=f"An error occurred while saving questions: {str(e)}")


# Test endpoint for checking database connection
@app.get("/test-db")
async def test_db():
    """
    Endpoint to test the MongoDB database connection.
    """
    try:
        # Attempt a simple operation to check if the database is accessible
        db.list_collection_names()
        return {"message": "Database connection successful"}
    except Exception as e:
        logger.error('Error occurred while connecting to the database: %s', str(e))
        raise HTTPException(status_code=500, detail="Database connection failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)

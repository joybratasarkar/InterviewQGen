from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
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

# Define the prompt template for generating interview questions
question_prompt_template = """
You are a professional interviewer tasked with creating interview questions for a job role. Based on the summarized job description provided below, generate a list of interview questions categorized into Easy, Medium, and Hard. Each category should include relevant and insightful questions that help assess the candidate's skills and fit for the role.

Job Description Summary:
{job_description_summary}

Questions:
- Easy:
- Medium:
- Hard:
"""

# Create a PromptTemplate instance for generating interview questions
question_prompt = PromptTemplate(template=question_prompt_template, input_variables=["job_description_summary"])

class JobDescription(BaseModel):
    description: str

# Create a thread pool executor for parallel processing
executor = ThreadPoolExecutor(max_workers=8)

@lru_cache(maxsize=100)
def get_cached_summary(job_description):
    return summarize_job_description(job_description)

async def summarize_job_description(job_description, chunk_size=512):
    # Check cache
    cached_summary = get_cached_summary(job_description)
    if cached_summary:
        return cached_summary

    # Split the job description into manageable chunks
    chunks = [job_description[i:i + chunk_size] for i in range(0, len(job_description), chunk_size)]
    
    # Use asyncio to parallelize summarization
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(executor, process_chunk, chunk) for chunk in chunks]
    summaries = await asyncio.gather(*tasks)
    
    # Combine all chunk summaries
    full_summary = " ".join(summaries)
    
    # Cache the result
    get_cached_summary.cache_set(job_description, full_summary)
    
    return full_summary

def process_chunk(chunk):
    inputs = tokenizer(chunk, return_tensors='pt', max_length=512, truncation=True)
    summary_ids = model.generate(
        inputs['input_ids'],
        max_length=100,
        min_length=30,
        length_penalty=1.0,
        num_beams=1,
        early_stopping=True
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
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
        print('summary',summary)
        questions = await generate_interview_questions(summary)
        logger.info('Generated Questions: %s', questions)
        return {"questions": questions}
    except Exception as e:
        logger.error('Error occurred: %s', str(e))
        raise HTTPException(status_code=500, detail=str(e))

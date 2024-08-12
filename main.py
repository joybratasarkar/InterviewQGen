from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from transformers import pipeline
import openai
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from the .env file
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Hugging Face summarization pipeline with an appropriate model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

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

def summarize_job_description(job_description):
    input_length = len(job_description.split())
    if input_length > 500:
        max_length = 150
        min_length = 50
    elif input_length > 300:
        max_length = 100
        min_length = 30
    else:
        max_length = 80
        min_length = 20
    summary = summarizer(job_description, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

def generate_interview_questions(job_description_summary):
    prompt = question_prompt.format(job_description_summary=job_description_summary)
    questions = llm(prompt)
    return questions.strip()

@app.post("/generate")
def generate(job_description: JobDescription):
    try:
        print('---------------------------------------')
        summary = summarize_job_description(job_description.description)
        questions = generate_interview_questions(summary)
        print('questions', questions)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""OpenAI Prompts"""


import os
import openai
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

_ = load_dotenv(find_dotenv())  # read local .env file  
openai.api_key = os.getenv('OPENAI_API_KEY')



client = OpenAI()




def get_completion_from_messages(messages, model="gpt-4o-mini", temperature=0, max_tokens=2000, current = ""):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens,
    )

    print(f"\n=== Token Usage ({current}) ===")
    print(f"Input: {response.usage.prompt_tokens}")
    print(f"Output: {response.usage.completion_tokens}")
    print(f"Total: {response.usage.total_tokens}")
    print("===================\n")

    return response.choices[0].message.content


output_schema = """
    {
    "skills": [],
    "experience": [],
    "education": [],
    "projects": [],
    "tools": []
    }

"""

def extract_resume_prompt(resume_content):

    delimiter = "```"

    system_message = f"""
    You will be provided with a resume. \
    Please extract skills, experience, education, projects, and tools from the resume and return them in a structured format. \
    
    Return ONLY valid JSON in the following format.

    {output_schema}


    Only output relevant information that would be useful for a job application. \
    If the resume contains irrelevant information, please ignore it. \
    The output will be used to match with a job posting description to see the match between the resume and description and determine and percentage match so only return useful information.
        """

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Here is the resume: {delimiter}{resume_content}{delimiter}"},
    ]

    return get_completion_from_messages(messages, current = "Extract Resume")

def extract_job_description_prompt(job_description_content):
    delimiter = "```"

    system_message = f"""
    You will be provided with a job description. \
    Please extract the extract required skills, experience, education, projects, and tools from the job description and return them in a structured format. \
    
    Return ONLY valid JSON in the following format.

    {output_schema}

    

    Only output relevant information that would be useful for a job application. \
    If the job description contains irrelevant information, please ignore it. \
    The output will be used to match with a resume description to see the match between the resume and description and determine and percentage match so only return useful information.
    """

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Here is the job description: {delimiter}{job_description_content}{delimiter}"},
    ]

    return get_completion_from_messages(messages, current = "Extract Job Description")


def calculate_match(extracted_resume, extracted_job_description):
    delimiter = "```"

    system_message = f"""
    You will be provided with an extracted resume and an extracted job description both in json. \
    Please compare the extracted information from the resume and job description and determine the percentage match between the two. \
    The percentage match should be based on the skills, experience, education, projects, and tools required by the job description and how well they match with the skills, experience, education, projects, and tools listed in the resume. \
    Only output the percentage match as a number between 0 and 100.

    For the grade, a score of 100% mean the resume is a perfect match for the job description in that category, while a score of 0% means there is no match at all. \
    Please provide a brief explanation for the match percentage in each category as well.

    The overall match should compare the overall match of the resume to the job description and not just the average of the skill, education and experience matches.
    
    Output in this order:

    Skill Match: %
    Experience Match: %
    Education Match: %
    Overall Match: %

    In addition list the Strong Matches, Missing Skills, Resume Recommendations/Suggestions, and some example Interview Questions.
    """

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Here is the extracted resume: {delimiter}{extracted_resume}{delimiter} Here is the extracted job description: {delimiter}{extracted_job_description}{delimiter}"},
    ]

    return get_completion_from_messages(messages, current = "Match")



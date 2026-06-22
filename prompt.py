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


import re
import json
import requests
import trafilatura
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def extract_all(url):
    headers = {

    "User-Agent": (
        "Mozilla/5.0"
    ),
    "Accept": "application/json, text/html"
    }
    
    response = requests.get(
        url,
        headers=headers
    )

    soup = BeautifulSoup(
    response.text,
    "html.parser"
    )
    
    return soup.get_text()

def valid_extraction(text):

    if not text:
        return False

    text  = text.strip().lower()

    if len(text) < 1200:
        return False
    
    bad_words = [
        "equal employment opportunity",
        "reasonable accommodation",
        "will not tolerate discrimination",
        "protected veteran",
        "without regard to race",
        "share on:",
        "all employees must be legally authorized"
    ]

    bad_hits = sum(1 for word in bad_words if word in text)

    if bad_hits >= 2:
        return False
    
    # Require real job-content signals
    useful_words = [
        "responsibilities",
        "qualifications",
        "requirements",
        "experience",
        "skills",
        "education",
        "python",
        "java",
        "sql",
        "software",
        "develop",
        "application",
        "cloud",
        "api"
    ]

    useful_hits = sum(1 for word in useful_words if word in text)

    if useful_hits < 4:
        return False
    
    # Reject if it looks like empty section headers
    empty_headers = [
        "responsibilities: skills: education",
        "responsibilities: skills:",
        "skills: education & experience"
    ]

    if any(pattern in text for pattern in empty_headers):
        return False

    return True


def extract_job_description(url):
    text = ""
    if "workday" in url:
        print("Workday Extraction")
        text = extract_workday(url)
    
    else:

        html = fetch_html(url)

        json_text = extract_json_job(html)

        if valid_extraction(json_text):
            print("JSON Extraction")
            return clean_and_trim(json_text)
        

        text = trafilatura.extract(html)

        if valid_extraction(text):
            return clean_and_trim(text)

        full_text = extract_all(url)

        return clean_and_trim(full_text)

        # if not text:
        #     soup = BeautifulSoup(html, "html.parser")
        #     text = soup.get_text("\n", strip=True)
    
    # if valid_extraction(text):
    #     print("HTML Extraction")
    #     return clean_and_trim(text)

    # else:
    #     print("Full Page Extraction")
    #     return clean_and_trim(extract_all(url))


def fetch_html(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    return response.text


def extract_main_content(html):
    text = trafilatura.extract(html)

    if text:
        return text
    
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n", strip=True)


def extract_json_job(html):

    soup = BeautifulSoup(html, "html.parser")

    for script in soup.find_all("script", type="application/ld+json"):

        try:
            data = json.loads(script.string)

            if isinstance(data, dict) and data.get("@type") == "JobPosting":
                desc_html = data.get("description", "")

                return BeautifulSoup(desc_html, "html.parser").get_text("\n", strip=True)
            # print(data)
            # print()
        
        except Exception:
            pass

    return None

def build_workday_api(url):
    parts = urlparse(url)

    tenant = parts.netloc.split(".")[0]
    segments = parts.path.strip("/").split("/")
    site = segments[0]

    job_path = "/".join(segments[1:])

    api = (
        f"{parts.scheme}://{parts.netloc}"
        f"/wday/cxs/{tenant}/{site}/{job_path}"
    )

    return api

def extract_workday(url):
    api_url = build_workday_api(url)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/html"
    }

    response = requests.get(api_url, headers=headers, timeout=20)
    response.raise_for_status()

    data = response.json()

    job_info = data.get("jobPostingInfo", {})

    title = job_info.get("title", "")
    location = job_info.get("location", "")
    description_html = job_info.get("jobDescription", "")

    description_text = BeautifulSoup(
        description_html,
        "html.parser"
    ).get_text("\n", strip=True)

    return f"""
    Title: {title}
    Location: {location}

    {description_text}
    """.strip()

def clean_and_trim(text):
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    start_markers = [
        "Job Description",
        "Responsibilities",
        "Skills",
        "Education",
        "Experience",
        "Position Overview",
        "About the role",
        "About this role",
        "Responsibilities",

    ]

    end_markers = [
        "Equal Opportunity Employer",
        "Apply Now",
        "Saved Jobs",
        "Jobs for You",
        "Recruitment Fraud",
        "Connect with us",
        "Follow Us",
        "Copyright",
        "Share on:",
        "All employees must be legally authorized",
        "If you need a reasonable accommodation",
        "RSA is committed to the principle"
    ]

    lower = text.lower()

    for marker in start_markers:
        index = lower.find(marker.lower())
        if index != -1:
            text = text[index:]
            break

    lower = text.lower()

    end_indexes = []

    for marker in end_markers:
        index = lower.find(marker.lower())
        if index != -1:
            end_indexes.append(index)

    if end_indexes:
        text = text[:min(end_indexes)]

    max_chars = 5000
    return text.strip()[:max_chars]

# test_html = fetch_html("https://jobs.boeing.com/job/-/-/185/96286214832?utm_source=linkedin&utm_medium=job_posting&utm_campaign=ra-us")
# test_html = fetch_html("https://reliaquest.wd5.myworkdayjobs.com/ReliaQuest_Careers/job/Tampa-FL/Associate-Software-Engineer_R15047?source=LinkedIn")
# test_main_content = extract_main_content(test_html)
# test_json_job = clean_and_trim(extract_json_job(test_html))

test = extract_job_description("https://jobs.boeing.com/job/-/-/185/96286214832?utm_source=linkedin&utm_medium=job_posting&utm_campaign=ra-us")
# test = extract_job_description("https://reliaquest.wd5.myworkdayjobs.com/ReliaQuest_Careers/job/Tampa-FL/Associate-Software-Engineer_R15047?source=LinkedIn")
print(test)




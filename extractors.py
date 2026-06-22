"""Extractions"""
import streamlit as st
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




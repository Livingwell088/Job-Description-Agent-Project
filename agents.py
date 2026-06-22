"""Agent Functions"""


import os

from extractors import extract_job_description
from prompt import calculate_match, extract_job_description_prompt, extract_resume_prompt
from storage import get_hash, save_job_to_json, save_resume_to_json

#     job = extractor_agent()
#     parsed_resume = resume_parser()
#     parsed_job = job_parser()
#     match = matcher()
#     advice = coach()
#     return advice


def coordinator_agent(url=None, paste=None):

    job_text = extractor_agent(url, paste)

    if not job_text:
        return {
            "status": "Needs Manual Paste",
            "message": "Could not extract job description"
        }
    
    resume_json = parser_agent_resume()
    job_json = parser_agent_job()
    report = matcher_agent(resume_json["data"], job_json["data"])

    return {
        "status": "success",
        "job_text": job_text,
        "resume_json": resume_json,
        "job_json": job_json,
        "report": report
    }

    # return report


def extractor_agent(url=None, pasted_text=None):

    if url:
        try:
            description = extract_job_description(url)
            return description
        except:

            if pasted_text:
                return pasted_text
            return None    
    
    if pasted_text:
        return pasted_text
    
    return None
    
def parser_agent_resume():
    if os.path.exists("files/resume_extracted.json") and os.path.exists("files/resume_hash.txt"):

        with open("files/resume.txt", "r", encoding="utf-8") as resume, \
            open("files/resume_hash.txt", "r", encoding="utf-8") as hash:
            
            if get_hash(resume.read()) == hash.read():
                pass
            else:
                save_resume_to_json()
    else:
        save_resume_to_json()

    try:
        with open("files/resume_extracted.json", "r", encoding="utf-8") as file:
            return {
                "status": "success",
                "data": file.read()
            }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


def parser_agent_job():
    if os.path.exists("files/job_extracted.json") and os.path.exists("files/job_hash.txt"):

        with open("files/job.txt", "r",encoding="utf-8") as job, \
            open("files/job_hash.txt", "r", encoding="utf-8") as hash:
            
            if get_hash(job.read()) == hash.read():
                pass                
            else:
                save_job_to_json()
    else:
        save_job_to_json()
    
    try:
        with open("files/job_extracted.json", "r", encoding="utf-8") as file:
            return {
                "status": "success",
                "data": file.read()
            }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


def matcher_agent(resume_json, job_json):

    try:
        report = calculate_match(resume_json, job_json)

        return {
            "status": "success",
            "data": report
        }
    
    except Exception as e:

        return {
            "status": "failed",
            "error": str(e)
        }






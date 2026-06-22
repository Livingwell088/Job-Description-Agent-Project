"""Save/Load/Hash Files"""

import hashlib
import json
from prompt import extract_job_description_prompt, extract_resume_prompt




def get_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


def save_resume_to_json():
    with open("files/resume.txt", "r", encoding="utf-8") as file, \
         open("files/resume_hash.txt", "w") as hash:
        resume_content = file.read()

        hashed = get_hash(resume_content)
        
    resume_result = json.loads(extract_resume_prompt(resume_content))
    
    with open("files/resume_extracted.json", "w") as file:
        json.dump(resume_result, file, indent=4)
    
    with open("files/resume_hash.txt", "w") as hash:
        hash.write(hashed)
    

def save_job_to_json():
    with open("files/job.txt", "r", encoding="utf-8") as file, \
         open("files/job_hash.txt", "w") as hash:
        job_description_content = file.read()

        hashed = get_hash(job_description_content)
        

    job_result = json.loads(extract_job_description_prompt(job_description_content))

    with open("files/job_extracted.json", "w") as file:
        json.dump(job_result, file, indent=4)
    
    with open("files/job_hash.txt", "w") as hash:
        hash.write(hashed)








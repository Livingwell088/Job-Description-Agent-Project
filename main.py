

import os

from prompt import calculate_match, extract_job_description, extract_job_description_prompt, extract_resume_prompt


import json
import hashlib


import requests
from bs4 import BeautifulSoup


resume_content = ""
job_description_content = ""


def get_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


def save_resume_to_json():
    with open("resume.txt", "r", encoding="utf-8") as file, \
         open("resume_hash.txt", "w") as hash:
        resume_content = file.read()

        hashed = get_hash(resume_content)
        


    resume_result = json.loads(extract_resume_prompt(resume_content))
    
    with open("resume_extracted.json", "w") as file:
        json.dump(resume_result, file, indent=4)
    
    with open("resume_hash.txt", "w") as hash:
        hash.write(hashed)
    

def save_job_to_json():
    with open("job.txt", "r", encoding="utf-8") as file, \
         open("job_hash.txt", "w") as hash:
        job_description_content = file.read()

        hashed = get_hash(job_description_content)
        

    job_result = json.loads(extract_job_description_prompt(job_description_content))

    with open("job_extracted.json", "w") as file:
        json.dump(job_result, file, indent=4)
    
    with open("job_hash.txt", "w") as hash:
        hash.write(hashed)




# def coordinator():

#     job = extractor_agent()

#     parsed_resume = resume_parser()

#     parsed_job = job_parser()

#     match = matcher()

#     advice = coach()

#     return advice

# def extractor_agent():




import streamlit as st


    


@st.cache_data
def cached_extract(url):

    try:
        description = extract_job_description(url)
        return description
    except:
        return None

st.set_page_config(
    page_title="Job Application Agent",
    layout="wide"
)

st.title("Job Application Agent")


# --- SESSION ---
defaults = {
    "job_text": None,
    "job_json": None,
    "report": None,
    "resume_json": None,
    "active_tab": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value



# --- SIDEBAR ---
with st.sidebar:
    st.header("Home")

    if st.button("Back to Home"):
        st.session_state.active_tab = "Home"
        st.rerun()

    st.divider()

    st.header("Resume")

    uploaded = st.file_uploader(
        "Upload Resume",
        type=["txt"]
    )

    if uploaded:
        text = uploaded.read().decode("utf-8")

        with open("resume.txt", "w", encoding="utf-8") as file:
            file.write(text)
        
        st.success("Resume Uploaded and Updated")

    st.divider()

    st.header("Settings")


# --- TABS ---
# extract_tab, match_tab = st.tabs([
#     "Extract",
#     "Match"
# ])

if "active_tab" not in st.session_state or st.session_state.active_tab == None:
    st.session_state.active_tab = "Home"

selected_tab = st.session_state.active_tab


if selected_tab == "Home":

    st.write("Job Description Agent")

    if st.button("Extract Description from Job"):
        st.session_state.active_tab = "Extract"
        st.rerun()
    
    if st.button("Match Resume with Job"):
        st.session_state.active_tab = "Match"
        st.rerun()


# --- EXTRACT ---
if selected_tab == "Extract":

    st.write("""Extract Job Descriptions""")

    url = st.text_input(
        "Enter Url ..."
    )

    st.write("OR")

    paste = st.text_area(
        "Paste Here ..."
    )

    if st.button("Extract Job"):

        with st.spinner("Extracting ..."):

            if url:
                st.write("TEST")
                job = cached_extract(url)

                if job == None:
                    if paste:
                        job = paste
                    else:
                        st.error("Please manually paste job description or try a valid url")
                

            else:
                job = paste
            
            st.session_state.job_text = job
        
        if st.session_state.job_text:
            st.success("Done")

        with open("job.txt", "w", encoding="utf-8") as file:
            file.write(st.session_state.job_text)


    if st.session_state.job_text:

        txt_tab, json_tab = st.tabs([
            "Text Description",
            "JSON Description"
        ])

        with txt_tab:
            st.write(st.session_state.job_text)
        
        with json_tab:

            if st.session_state.job_json:

                st.json(st.session_state.job_json)
            
            else:

                st.info("Run Match to generate te extracted JSON")
        
        if st.button("Go to Match"):
            st.session_state.active_tab = "Match"
            st.rerun()

            


# --- MATCH ---

if selected_tab == "Match":

    col1, col2 = st.columns(2)

    if st.button("Match"):
        with st.spinner("Extracting ..."):

            if os.path.exists("resume_extracted.json") and os.path.exists("resume_hash.txt"):

                with open("resume.txt", "r", encoding="utf-8") as resume, \
                    open("resume_hash.txt", "r", encoding="utf-8") as hash:
                    
                    if get_hash(resume.read()) == hash.read():
                        print("Resume File exists")
                    else:
                        save_resume_to_json()
            else:
                print("File not found")
                save_resume_to_json()
            
            if os.path.exists("resume_extracted.json") and os.path.getsize("resume_extracted.json") > 0:
                with open("resume_extracted.json", "r", encoding="utf-8") as file:
                    st.session_state.resume_json = json.load(file)
            else:
                st.error("resume_extracted.json is empty")

            if os.path.exists("job_extracted.json") and os.path.exists("job_hash.txt"):

                with open("job.txt", "r",encoding="utf-8") as job, \
                    open("job_hash.txt", "r", encoding="utf-8") as hash:
                    
                    if get_hash(job.read()) == hash.read():
                        st.write("Report of this job description already saved")
                        
                    else:
                        save_job_to_json()
            else:
                save_job_to_json()

            if os.path.exists("job_extracted.json") and os.path.getsize("job_extracted.json") > 0:
                with open("job_extracted.json", "r", encoding="utf-8") as file:
                    st.session_state.job_json = json.load(file)
            else:
                st.error("job_extracted.json is empty")


            with open("resume_extracted.json", "r", encoding="utf-8") as resume_file, \
                open("job_extracted.json", "r", encoding="utf-8") as job_file:

                extracted_resume = resume_file.read()
                extracted_job = job_file.read()

                resume_and_description_match = calculate_match(extracted_resume, extracted_job)
                # print(resume_and_description_match)

                with open("report.md", "w", encoding="utf-8") as file:
                    file.write(resume_and_description_match)
                st.session_state.report = resume_and_description_match

    

    with col1:
        st.subheader("Resume")

        if st.session_state.resume_json:
            st.json(st.session_state.resume_json)
        
    
    with col2:
        st.subheader("Job")

        if st.session_state.job_json:
            st.json(st.session_state.job_json)
    
    
    if st.session_state.report:
        st.markdown(st.session_state.report)
        st.download_button(
        "Download Report",
        st.session_state.report,
        "report.md"
    )

# from urllib.parse import urlparse

# import panel as pn
# import time
# pn.extension()

# # pn.pane.Markdown("## Job Application Agent")

# url_input = pn.widgets.TextInput(name="URL", placeholder="Paste the job URL here...")
# extract_button = pn.widgets.Button(name="Extract Job Description Info")
# extracted_output = pn.pane.Markdown("Waiting for URL...")

# def extract_on_click(event):
#     url = url_input.value

#     result = extract_job_description(url)

#     extracted_output.object = "Job Description saved to job.txt \n\n\n" + result

#     with open("job.txt", "w", encoding="utf-8") as file:
#         file.write(result)



# match_button = pn.widgets.Button(name="Match Resume with Job Description.")
# match_output = pn.pane.Markdown("Waiting to match...")

# def match_on_click(event):

#     if os.path.exists("resume_extracted.json") and os.path.exists("resume_hash.txt"):

#         with open("resume.txt", "r", encoding="utf-8") as resume, \
#             open("resume_hash.txt", "r", encoding="utf-8") as hash:
            
#             if get_hash(resume.read()) == hash.read():
#                 print("Resume File exists")
#             else:
#                 save_resume_to_json()
#     else:
#         print("File not found")
#         save_resume_to_json()
        

#     if os.path.exists("job_extracted.json") and os.path.exists("job_hash.txt"):

#         with open("job.txt", "r",encoding="utf-8") as job, \
#             open("job_hash.txt", "r", encoding="utf-8") as hash:
            
#             if get_hash(job.read()) == hash.read():
#                 print("Job File Exists")
#                 match_output.object = "Job Description Matching already done and saved to report.md"
#                 time.sleep(3)
#                 server.stop()
            
#             else:
#                 save_job_to_json()
#     else:
#         print("File not found")
#         save_job_to_json()


#     with open("resume_extracted.json", "r", encoding="utf-8") as resume_file, \
#         open("job_extracted.json", "r", encoding="utf-8") as job_file:

#         extracted_resume = resume_file.read()
#         extracted_job = job_file.read()

#         resume_and_description_match = calculate_match(extracted_resume, extracted_job)
#         # print(resume_and_description_match)

#         with open("report.md", "w", encoding="utf-8") as file:
#             file.write(resume_and_description_match)
#         match_output.object = resume_and_description_match



# extract_button.on_click(extract_on_click)

# extract_page = pn.Column(
#     "## Job Application Agent",
#     url_input,
#     extract_button,
#     extracted_output
# )

# match_button.on_click(match_on_click)

# match_page = pn.Column(
#     "## Match Resume and Job Description",
#     match_button,
#     match_output
# )



# app = pn.Tabs(
#     ("Extraction", extract_page),
#     ("Match", match_page)
# )

# server = app.show()


    


"""Streamlit"""

import json
import os

from agents import coordinator_agent, extractor_agent
# from extractors import extract_job_description
# from prompt import calculate_match



import requests
from bs4 import BeautifulSoup




import streamlit as st

from storage import get_hash, save_job_to_json, save_resume_to_json


@st.cache_data
def cached_extract(url, pasted):
    return extractor_agent(url, pasted)

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

            job = cached_extract(url, paste)

            if job == None:
                st.error("Please manually paste job description or try a valid url")

            # if url:
            #     st.write("TEST")
            #     job = cached_extract(url)

            #     if job == None:
            #         if paste:
            #             job = paste
            #         else:
            #             st.error("Please manually paste job description or try a valid url")
                

            # else:
            #     job = paste
            
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
        with st.spinner("Running Agent ..."):

            result = coordinator_agent(url=None, paste=st.session_state.job_text)

            if result["status"] != "success":
                st.error(result.get("message", result.get("error")))
            else:
                st.session_state.report = result["report"]["data"]
                
            
            if os.path.exists("files/resume_extracted.json") and os.path.getsize("files/resume_extracted.json") > 0:
                with open("files/resume_extracted.json", "r", encoding="utf-8") as file:
                    st.session_state.resume_json = json.load(file)
            else:
                st.error("files/resume_extracted.json is empty")


            if os.path.exists("files/job_extracted.json") and os.path.getsize("files/job_extracted.json") > 0:
                with open("files/job_extracted.json", "r", encoding="utf-8") as file:
                    st.session_state.job_json = json.load(file)
            else:
                st.error("files/job_extracted.json is empty")


            # with open("files/resume_extracted.json", "r", encoding="utf-8") as resume_file, \
            #     open("files/job_extracted.json", "r", encoding="utf-8") as job_file:

            #     extracted_resume = resume_file.read()
            #     extracted_job = job_file.read()

            #     resume_and_description_match = calculate_match(extracted_resume, extracted_job)
            #     # print(resume_and_description_match)

            #     with open("files/report.md", "w", encoding="utf-8") as file:
            #         file.write(resume_and_description_match)
            #     st.session_state.report = resume_and_description_match

    

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

import streamlit as st
import os
import fitz
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini = genai.GenerativeModel("gemini-1.5-flash")


@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


model = load_model()


def extract_text(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    return splitter.split_text(text)


def build_index(chunks):
    client = chromadb.Client()
    try:
        client.delete_collection("resume")
    except Exception:
        pass
    collection = client.create_collection("resume")
    embeddings = model.encode(chunks).tolist()
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    return collection


def retrieve(collection, query, top_k=5):
    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)
    return results["documents"][0]


def analyze(chunks, job_description):
    context = "\n\n".join(chunks)
    prompt = f"""
You are an expert ATS system and career coach.

RESUME SECTIONS (most relevant to this job):
{context}

JOB DESCRIPTION:
{job_description}

Based ONLY on the resume sections above, provide:
1. MATCH SCORE: 0-100% with one sentence of reasoning
2. PROFILE SUMMARY: 2-3 line recruiter-style summary
3. STRENGTHS: 3 specific strengths relevant to this JD
4. GAPS: 3 missing skills or weaknesses for this role
5. SUGGESTIONS: 3 specific resume improvements for this JD

Be precise. Never invent skills not present in the context.
"""
    response = gemini.generate_content(prompt)
    return response.text


st.set_page_config(
    page_title="RAG Resume Analyzer",
    page_icon="\U0001F4C4",
    layout="wide"
)

st.title("RAG Resume Analyzer")
st.caption("Retrieval-Augmented Generation + Google Gemini 1.5 Flash + ChromaDB")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Resume (PDF only)", type="pdf")

with col2:
    job_description = st.text_area("Paste Job Description here", height=250)

if st.button("Analyze Resume", use_container_width=True):
    if not uploaded_file or not job_description.strip():
        st.warning("Both resume and job description are required.")
        st.stop()

    with st.spinner("Step 1 of 4: Extracting text from PDF..."):
        resume_text = extract_text(uploaded_file)

    with st.spinner("Step 2 of 4: Splitting into chunks..."):
        chunks = chunk_text(resume_text)

    with st.spinner("Step 3 of 4: Building vector index..."):
        collection = build_index(chunks)

    with st.spinner("Step 4 of 4: Retrieving and analyzing with Gemini..."):
        relevant = retrieve(collection, job_description)
        result = analyze(relevant, job_description)

    st.success("Analysis complete!")
    st.markdown("---")
    st.markdown(result)

    with st.expander("RAG Transparency: View Retrieved Chunks"):
        st.caption("These are the exact resume sections Gemini received. Not the full resume.")
        for i, chunk in enumerate(relevant):
            st.markdown(f"**Chunk {i+1}**")
            st.info(chunk)

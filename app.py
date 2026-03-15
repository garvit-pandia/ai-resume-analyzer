import streamlit as st
import os
import fitz
import chromadb
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

load_dotenv()

# ── LLM Provider Setup ──────────────────────────────────────────────────────

PROVIDERS = {
    "Gemini 1.5 Flash (Google)": {
        "env_key": "GEMINI_API_KEY",
        "description": "🔵 Best for: Reliability, long documents, production use",
    },
    "LLaMA 3.3 70B (Groq)": {
        "env_key": "GROQ_API_KEY",
        "description": "⚡ Best for: Speed — fastest inference available (~500+ tok/s)",
    },
}


def call_gemini(prompt):
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


def call_groq(prompt):
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048,
    )
    return response.choices[0].message.content


LLM_DISPATCH = {
    "Gemini 1.5 Flash (Google)": call_gemini,
    "LLaMA 3.3 70B (Groq)": call_groq,
}


# ── Embedding Model ─────────────────────────────────────────────────────────

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


embed_model = load_embedding_model()


# ── Core Functions ───────────────────────────────────────────────────────────

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
    embeddings = embed_model.encode(chunks).tolist()
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    return collection


def retrieve(collection, query, top_k=5):
    query_embedding = embed_model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)
    return results["documents"][0]


def build_prompt(context, job_description):
    return f"""
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


def analyze(chunks, job_description, provider):
    context = "\n\n".join(chunks)
    prompt = build_prompt(context, job_description)
    return LLM_DISPATCH[provider](prompt)


# ── Streamlit UI ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="RAG Resume Analyzer",
    page_icon="\U0001F4C4",
    layout="wide"
)

# ── Sidebar: Provider Selection ──────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ LLM Provider")
    provider = st.radio(
        "Choose your LLM backend:",
        list(PROVIDERS.keys()),
        index=0,
        help="Switch between providers without redeploying.",
    )
    st.caption(PROVIDERS[provider]["description"])

    # API key status indicator
    env_key = PROVIDERS[provider]["env_key"]
    key_present = bool(os.getenv(env_key))
    if key_present:
        st.success(f"✅ `{env_key}` detected")
    else:
        st.error(f"❌ `{env_key}` not found — add it to .env or HF Secrets")

    st.divider()
    st.caption("**Provider Comparison**")
    st.markdown("""
    | | Gemini | Groq |
    |---|---|---|
    | Speed | Fast | ⚡ Ultra-fast |
    | Context | 1M tokens | 128K tokens |
    | Model | Gemini 1.5 Flash | LLaMA 3.3 70B |
    | Cost | Pro plan | Free tier |
    """)

# ── Main Content ─────────────────────────────────────────────────────────────

st.title("RAG Resume Analyzer")
provider_label = "Groq LLaMA 3.3" if "Groq" in provider else "Google Gemini 1.5 Flash"
st.caption(f"RAG + ChromaDB + sentence-transformers → **{provider_label}**")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Resume (PDF only)", type="pdf")

with col2:
    job_description = st.text_area("Paste Job Description here", height=250)

if st.button("Analyze Resume", type="primary", use_container_width=True):
    if not uploaded_file or not job_description.strip():
        st.warning("Both resume and job description are required.")
        st.stop()

    if not os.getenv(PROVIDERS[provider]["env_key"]):
        st.error(f"Missing API key: `{PROVIDERS[provider]['env_key']}`. Add it to .env or HF Spaces Secrets.")
        st.stop()

    with st.spinner("Step 1 of 4: Extracting text from PDF..."):
        resume_text = extract_text(uploaded_file)

    with st.spinner("Step 2 of 4: Splitting into chunks..."):
        chunks = chunk_text(resume_text)

    with st.spinner("Step 3 of 4: Building vector index..."):
        collection = build_index(chunks)

    with st.spinner(f"Step 4 of 4: Analyzing with {provider_label}..."):
        relevant = retrieve(collection, job_description)
        result = analyze(relevant, job_description, provider)

    st.success(f"Analysis complete via **{provider_label}**!")
    st.markdown("---")
    st.markdown(result)

    with st.expander("RAG Transparency: View Retrieved Chunks"):
        st.caption("These are the exact resume sections the LLM received. Not the full resume.")
        for i, chunk in enumerate(relevant):
            st.markdown(f"**Chunk {i+1}**")
            st.info(chunk)

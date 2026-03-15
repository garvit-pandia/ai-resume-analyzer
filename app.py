import streamlit as st
import os
import fitz
import chromadb
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

load_dotenv()

# ── Model Definitions ────────────────────────────────────────────────────────

GEMINI_MODELS = {
    "Gemini 2.5 Flash ⭐ (Recommended)": "gemini-2.5-flash",
    "Gemini 2.5 Pro (Deep Reasoning)": "gemini-2.5-pro",
    "Gemini 2.5 Flash-Lite (Budget)": "gemini-2.5-flash-lite",
}

GROQ_MODELS = {
    "GPT-OSS 120B ⭐ (Best Quality)": "openai/gpt-oss-120b",
    "LLaMA 3.3 70B (Versatile)": "llama-3.3-70b-versatile",
    "GPT-OSS 20B (Ultra-Fast)": "openai/gpt-oss-20b",
    "LLaMA 3.1 8B (Instant)": "llama-3.1-8b-instant",
}

PROVIDERS = {
    "Google (Gemini)": {
        "env_key": "GEMINI_API_KEY",
        "models": GEMINI_MODELS,
        "icon": "🔵",
        "description": "1M context, reasoning, stable — best with your Pro plan",
    },
    "Groq (Ultra-Fast)": {
        "env_key": "GROQ_API_KEY",
        "models": GROQ_MODELS,
        "icon": "⚡",
        "description": "500-1000 tok/s speed, free tier, 128K context",
    },
}


# ── LLM Call Functions ───────────────────────────────────────────────────────

def call_gemini(prompt, model_id):
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(model_id)
    response = model.generate_content(prompt)
    return response.text


def call_groq(prompt, model_id):
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048,
    )
    return response.choices[0].message.content


LLM_DISPATCH = {
    "Google (Gemini)": call_gemini,
    "Groq (Ultra-Fast)": call_groq,
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


def analyze(chunks, job_description, provider, model_id):
    context = "\n\n".join(chunks)
    prompt = build_prompt(context, job_description)
    return LLM_DISPATCH[provider](prompt, model_id)


# ── Streamlit UI ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="RAG Resume Analyzer",
    page_icon="\U0001F4C4",
    layout="wide"
)

# ── Sidebar: Provider + Model Selection ──────────────────────────────────────

with st.sidebar:
    st.header("⚙️ LLM Settings")

    provider = st.radio(
        "Provider:",
        list(PROVIDERS.keys()),
        index=0,
        help="Switch between Google Gemini and Groq inference.",
    )

    provider_info = PROVIDERS[provider]
    st.caption(f"{provider_info['icon']} {provider_info['description']}")

    # Model selector for the chosen provider
    model_options = provider_info["models"]
    selected_model_label = st.selectbox(
        "Model:",
        list(model_options.keys()),
        index=0,
        help="Pick a specific model. ⭐ = recommended for this app.",
    )
    selected_model_id = model_options[selected_model_label]
    st.code(selected_model_id, language=None)

    # API key status
    env_key = provider_info["env_key"]
    key_present = bool(os.getenv(env_key))
    if key_present:
        st.success(f"✅ `{env_key}` detected")
    else:
        st.error(f"❌ `{env_key}` not found — add it to .env or HF Secrets")

    st.divider()
    st.caption("**Quick Comparison**")
    st.markdown("""
| | Gemini 2.5 Flash | GPT-OSS 120B |
|---|---|---|
| Speed | ~300 tok/s | ~500 tok/s |
| Context | 1M tokens | 128K tokens |
| Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Cost | Pro plan | Free tier |
    """)

# ── Main Content ─────────────────────────────────────────────────────────────

st.title("RAG Resume Analyzer")
st.caption(f"RAG + ChromaDB + sentence-transformers → **{selected_model_label.split(' (')[0]}** via {provider.split(' (')[0]}")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Resume (PDF only)", type="pdf")

with col2:
    job_description = st.text_area("Paste Job Description here", height=250)

if st.button("Analyze Resume", type="primary", use_container_width=True):
    if not uploaded_file or not job_description.strip():
        st.warning("Both resume and job description are required.")
        st.stop()

    if not os.getenv(provider_info["env_key"]):
        st.error(f"Missing API key: `{provider_info['env_key']}`. Add it to .env or HF Spaces Secrets.")
        st.stop()

    with st.spinner("Step 1 of 4: Extracting text from PDF..."):
        resume_text = extract_text(uploaded_file)

    with st.spinner("Step 2 of 4: Splitting into chunks..."):
        chunks = chunk_text(resume_text)

    with st.spinner("Step 3 of 4: Building vector index..."):
        collection = build_index(chunks)

    with st.spinner(f"Step 4 of 4: Analyzing with {selected_model_label.split(' (')[0]}..."):
        relevant = retrieve(collection, job_description)
        result = analyze(relevant, job_description, provider, selected_model_id)

    st.success(f"Analysis complete via **{selected_model_label}**!")
    st.markdown("---")
    st.markdown(result)

    with st.expander("RAG Transparency: View Retrieved Chunks"):
        st.caption("These are the exact resume sections the LLM received. Not the full resume.")
        for i, chunk in enumerate(relevant):
            st.markdown(f"**Chunk {i+1}**")
            st.info(chunk)

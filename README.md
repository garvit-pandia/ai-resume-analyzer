---
title: RAG Resume Analyzer
emoji: "\U0001F4C4"
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.36.0
app_file: app.py
pinned: false
license: mit
short_description: AI-powered resume analyzer using RAG, ChromaDB, and Gemini
tags:
  - rag
  - resume
  - chromadb
  - gemini
  - streamlit
  - nlp
---

# RAG Resume Analyzer

Upload a PDF resume and paste a job description. The app retrieves the most relevant 
resume sections using semantic search (ChromaDB + sentence-transformers) and sends 
them to Google Gemini 1.5 Flash for structured ATS-style analysis.

## How RAG works here
Instead of sending the full resume to Gemini, the app splits it into 300-character chunks, 
embeds each chunk using the all-MiniLM-L6-v2 model, then retrieves only the top 5 chunks 
most semantically similar to the job description. Only those chunks go to Gemini. This 
reduces noise and keeps analysis grounded in what actually matters for the role.

## Tech stack
| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| PDF parsing | PyMuPDF (fitz) |
| Chunking | LangChain RecursiveCharacterTextSplitter |
| Embeddings | sentence-transformers all-MiniLM-L6-v2 |
| Vector store | ChromaDB (in-memory) |
| LLM | Google Gemini 1.5 Flash |
| Deployment | Hugging Face Spaces |

## Run locally
```bash
git clone https://huggingface.co/spaces/YOUR_HF_USERNAME/rag-resume-analyzer
cd rag-resume-analyzer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Add your Gemini API key to .env: GEMINI_API_KEY=your_key_here
streamlit run app.py
```

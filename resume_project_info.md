# Portfolio Project: RAG-Powered Resume Analyzer

### Overview
A high-performance Recruitment Technology (RecTech) application that uses Retrieval-Augmented Generation (RAG) to perform semantic analysis on resumes against job descriptions. The system provides objective recruitment metrics, profile summaries, and actionable gap analysis using state-of-the-art Large Language Models (LLMs).

### Core Features
*   **Intelligent Text Processing**: Automates PDF extraction and recursive text chunking to preserve semantic context.
*   **Hybrid LLM Provider Support**: Dual integration with **Google Gemini (via AI Studio)** and **Groq Cloud**, allowing users to toggle between deep reasoning (1M+ context) and ultra-fast (500-1000 tok/s) inference.
*   **Vector Database Integration**: Uses **ChromaDB** for local vector storage and semantic search, ensuring relevant context is retrieved for LLM analysis.
*   **Advanced ATS Metrics**: Generates a 0-100% match score, recruiter-style summaries, and detailed SWOT analysis (Strengths, Weaknesses, Gaps).
*   **Premium Neumorphic UI**: Implemented a bespoke "Soft Surface" aesthetic with tactile micro-interactions, custom CSS-based typography (Newsreader/Inter), and a centered "Glass Card" layout for enhanced UX.

### Tech Stack
*   **Frontend**: Streamlit, Custom CSS/HTML, Google Fonts API.
*   **Generative AI**: Groq (Llama-3/GPT-OSS), Google Gemini 2.5 Pro/Flash.
*   **Orchestration & NLP**: LangChain (Recursive Splitters), Sentence-Transformers (all-MiniLM-L6-v2).
*   **Vector DB**: ChromaDB.
*   **Tools/DevOps**: Python, PyMuPDF (fitz), Git, Hugging Face Spaces (Deployment).

### Professional Bullet Points (For Resume)
*   Developed a full-stack Retrieval-Augmented Generation (RAG) application to automate resume screening, achieving sub-second analysis times using Groq API integration.
*   Engineered a semantic search pipeline using ChromaDB and Sentence-Transformers to retrieve job-critical context from PDF resumes with high precision.
*   Designed and implemented a custom Neumorphic UI using Streamlit and CSS, improving user engagement and visual differentiation from standard AI applications.
*   Integrated multi-provider LLM support (Google AI & Groq), optimizing the balance between computational cost, inference speed, and reasoning depth.
*   Automated extraction and processing of unstructured PDF data using PyMuPDF, feeding into a recursive splitting logic to maintain document hierarchy for LLM context.

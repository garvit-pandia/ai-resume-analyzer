# 🚀 AI Resume Analyzer

A powerful, Streamlit-based application that uses **Google Gemini AI** to analyze resumes against job descriptions. It provides instant feedback, match scores, and actionable advice to help you land your dream job.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## ✨ Features

*   **Smart Matching:** Calculates a relevance score (0-100%) for your resume based on the Job Description (JD).
*   **Vibes Summary:** Generates a snappy, recruitment-style summary of your profile.
*   **Strengths & Weaknesses:** Identifies 3 key strengths and 3 specific areas for improvement.
*   **Free to Use:** Powered by Google's generous free tier for the Gemini API.
*   **Privacy Focused:** No data is stored; resumes are processed in memory and discarded.

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/garvit-pandia/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up API Key
1.  Get your **FREE** API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Create a `.env` file in the root directory:
    ```bash
    touch .env  # or create manually on Windows
    ```
3.  Add your key:
    ```env
    GEMINI_API_KEY=your_api_key_starting_with_AIza...
    ```

### 4. Run the App
```bash
streamlit run app.py
```

## 📚 User Guide & Deployment

For detailed instructions on how to use the app or deploy it to Streamlit Cloud, check out the **[USER_GUIDE.md](USER_GUIDE.md)**!

## 🛠️ Tech Stack

*   **Frontend:** Streamlit
*   **AI Engine:** Google Gemini (via `google-generativeai`)
*   **PDF Processing:** PyPDF2
*   **Environment:** Python-dotenv

## 📄 License
MIT License

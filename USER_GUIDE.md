# AI Resume Analyzer - User Guide 🚀

Welcome to the AI Resume Analyzer! This tool helps you optimize your resume for specific job descriptions using Google's powerful Gemini AI.

## 1. Prerequisites 🛠️

Before you begin, ensure you have:
*   A Google Account (e.g., your student email).
*   A PDF version of your resume.
*   The Job Description (JD) text you want to apply for.

## 2. Get Your Free Google API Key 🔑

To use this app, you need a **Gemini API Key**. It's free and easy to get!

1.  Go to **[Google AI Studio](https://aistudio.google.com/app/apikey)**.
2.  Click on the **"Create API key"** button.
3.  Select your Google Cloud project (or let it create a new one for you).
4.  Copy the generated key (it starts with `AIza...`).

> **Tip for Students:** Google offers generous free usage limits for students and developers. You likely won't hit the daily cap unless you are analyzing thousands of resumes!

## 3. Configure the App ⚙️

### Option A: Running Locally
1.  Open the `.env` file in the project folder.
2.  Paste your key like this:
    ```env
    GEMINI_API_KEY=AIzaSyD...your_actual_key_here...
    ```
3.  Save the file.

### Option B: Deploying on Streamlit Cloud
1.  Go to your app dashboard on [share.streamlit.io](https://share.streamlit.io).
2.  Click the **Menu (⋮)** next to your app -> **Settings**.
3.  Go to the **Secrets** section.
4.  Add your key in the box:
    ```toml
    GEMINI_API_KEY = "AIzaSyD...your_actual_key_here..."
    ```
5.  Click **Save**. The app will reboot automatically.

## 4. How to Use the App 📝

1.  **Paste Job Description:** Copy the full text of the job posting you are interested in and paste it into the left text box.
2.  **Upload Resume:** Drag and drop your PDF resume into the right-hand uploader.
3.  **Click "Analyze Match":** Hit the rocket button! 🚀

### What You Get:
*   **Match Score (0-100):** How well your resume fits the role.
*   **Vibes Summary:** A quick, informal summary of how a recruiter might see you.
*   **Strengths:** 3 key things your resume does well.
*   **Weaknesses:** 3 specific areas to improve (missing keywords, formatting, etc.).

## 5. Troubleshooting ❓

*   **"Analysis Failed":** This usually means the API is busy or your key is invalid. Refresh the page and try again.
*   **"Configuration Error":** Double-check your API key in the `.env` file or Streamlit Secrets.

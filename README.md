# 📑 DocuBot AI  
DocuBot AI is a Streamlit-based web application that helps users upload `.txt`, `.pdf`, or `.docx` documents and receive simplified summaries, readability scores, word clouds, and even definitions of legal terms using AI tools like Gemini and HuggingFace.

## 🚀 Features  
- 📄 Upload and read `.txt`, `.pdf`, and `.docx` files.  
- 🧠 Summarize large text using HuggingFace transformers.  
- 📊 Get word counts, sentence counts, paragraph counts, and readability scores.  
- 🔤 See the most common words and download CSV stats.  
- ☁️ View WordClouds of uploaded text.  
- 📚 Understand legal terms using dictionary API and Google fallback.  
- 🤖 Chat with Gemini Pro for document-related queries.  
- 💬 Built-in sidebar chatbot for quick questions.

## 🛠️ Tech Stack  
**Frontend:** Streamlit  
**Backend:** Python  
**AI Models:** Google Gemini Pro, HuggingFace Transformers  
**Text Analysis:** `textstat`, `collections`, `wordcloud`  
**Document Parsing:** `docx`, `PyPDF2`

## 📦 Installation  
git clone https://github.com/G-Madhuri/DocuBot-AI.git  
cd DocuBot-AI  
pip install streamlit pandas textstat wordcloud matplotlib transformers python-docx PyPDF2 requests google-generativeai
pip install torch

## 👉 Update your Gemini API key inside app.py:

genai.configure(api_key="YOUR_API_KEY_HERE")
streamlit run app.py

## 📁 File Structure
bash
Copy
Edit
DocuBot-AI/  
├── app.py                 # Main Streamlit app  
└── README.md              # Project documentation  


🌟 Credits
Developed by Madhuri Gottumukkala and Srivarsha Chivukula
Powered by Streamlit, HuggingFace, Gemini Pro, and open-source 

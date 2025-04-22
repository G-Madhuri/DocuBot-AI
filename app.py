import streamlit as st
import pandas as pd
from collections import Counter
from textstat import flesch_kincaid_grade
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from transformers import pipeline
import docx
import PyPDF2
import requests
import google.generativeai as genai

# ----------------- INITIAL SESSION STATE -----------------
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""
if "text" not in st.session_state:
    st.session_state.text = None
if "final_summary" not in st.session_state:
    st.session_state.final_summary = None
if "hide_msg" not in st.session_state:
    st.session_state.hide_msg = False
if "last_uploaded" not in st.session_state:
    st.session_state.last_uploaded = None

# ----------------- GEMINI CONFIG -----------------
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("models/gemini-1.5-pro")

# ----------------- LEGAL TERM EXPLAINER -----------------
def explain_legal_term(term):
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{term.lower()}"
        response = requests.get(url)
        data = response.json()
        definition = data[0]['meanings'][0]['definitions'][0]['definition']
        return definition
    except Exception:
        google_search_url = f"https://www.google.com/search?q=legal+term+{term}"
        st.sidebar.markdown(
            f"❌ Couldn't find a definition for **{term}** via the dictionary API.<br>"
            f"<a href='{google_search_url}' target='_blank'>🔎 Search on Google</a>",
            unsafe_allow_html=True
        )
        return None

# ----------------- SIDEBAR CHAT & LEGAL TOOL -----------------
st.sidebar.header("📚 Legal Term Explainer")
query = st.sidebar.text_input("Enter a legal term:")
if query:
    meaning = explain_legal_term(query)
    if meaning:
        st.sidebar.markdown(f"**Definition of '{query}':**")
        st.sidebar.write(meaning)

if st.sidebar.button("💬 More queries?"):
    st.session_state.show_chat = not st.session_state.show_chat

if st.session_state.show_chat:
    st.sidebar.markdown("### 🤖 Chat Assistant")
    for user, bot in st.session_state.chat_history:
        st.sidebar.markdown(f"**You:** {user}")
        st.sidebar.markdown(f"**Bot:** {bot}")
    st.session_state.chat_input = st.sidebar.text_input("Your message", value=st.session_state.chat_input)
    send_clicked = st.sidebar.button("Send")
    if send_clicked:
        user_input = st.session_state.chat_input.strip()
        if user_input:
            try:
                response = model.generate_content(user_input)
                reply = response.text
            except Exception as e:
                reply = f"⚠️ Error: {str(e)}"
            st.session_state.chat_history.append((user_input, reply))
            st.session_state.chat_input = ""

# ----------------- NLP HELPERS -----------------
summarizer = pipeline("summarization")

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text() or ''
    return text

def chunk_text(text, max_words=500):
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

# ----------------- MAIN INTERFACE -----------------
st.title("📑 DocuBot AI")
uploaded_file = st.file_uploader("Upload a .txt, .pdf, or .docx file", type=["txt", "pdf", "docx"])

if uploaded_file:
    if st.session_state.last_uploaded != uploaded_file.name:
        if uploaded_file.name.endswith(".txt"):
            text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".docx"):
            text = extract_text_from_docx(uploaded_file)
        elif uploaded_file.name.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded_file)
        else:
            st.error("Unsupported file format.")
            st.stop()
        
        # Reset session states
        st.session_state.text = text
        st.session_state.final_summary = None
        st.session_state.hide_msg = False
        st.session_state.last_uploaded = uploaded_file.name
    else:
        text = st.session_state.text

    # Text Stats
    word_count = len(text.split())
    sentence_count = text.count('.') + text.count('!') + text.count('?')
    paragraph_count = sum(1 for para in text.split('\n') if para.strip() != '')
    character_count = len(text)
    readability_score = flesch_kincaid_grade(text)
    common_words = Counter(text.split()).most_common(10)

    if st.button("Summarize Text"):
        try:
            with st.spinner("Summarizing... Please wait."):
                chunks = chunk_text(text, max_words=500)
                summaries = []
                for chunk in chunks:
                    summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
                    summaries.append(summary)
                final_summary = " ".join(summaries)
                st.session_state.final_summary = final_summary
                st.session_state.hide_msg = True
        except Exception as e:
            st.error(f"An error occurred: {e}")

    if st.session_state.final_summary:
        st.subheader("📝 Summary:")
        st.write(st.session_state.final_summary)
        st.download_button("Download Summary", st.session_state.final_summary, file_name="summary.txt")

    st.subheader("📊 Text Analysis")
    st.write(f"Words: {word_count}")
    st.write(f"Sentences: {sentence_count}")
    st.write(f"Paragraphs: {paragraph_count}")
    st.write(f"Characters: {character_count}")
    st.write(f"Readability Score: {readability_score:.2f}")

    st.subheader("🔤 Most Common Words")
    df_common = pd.DataFrame(common_words, columns=["Word", "Count"])
    st.write(df_common)

    st.subheader("☁️ Word Cloud")
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)

    stats = {
        "Metric": ["Words", "Sentences", "Paragraphs", "Characters", "Readability Score"],
        "Count": [word_count, sentence_count, paragraph_count, character_count, readability_score]
    }
    df_stats = pd.DataFrame(stats)
    csv = df_stats.to_csv(index=False).encode('utf-8')
    st.download_button("Download Text Stats as CSV", csv, "text_stats.csv", "text/csv")

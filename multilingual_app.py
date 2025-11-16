# import streamlit as st
# from openai import OpenAI
# from gtts import gTTS
# import pandas as pd
# import PyPDF2
# import io
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # Streamlit page setup
# st.set_page_config(page_title="🌐 Multilingual Translator & TTS", page_icon="🎙️", layout="wide")
# st.title("🌐 Multilingual Translator & Text-to-Speech App")
# st.write("Upload a document or enter text, translate it into your preferred language, and listen to the result!")

# # --- INPUT SECTION ---
# input_option = st.radio("Choose Input Type:", ("✍️ Enter Text", "📂 Upload File"))

# text_data = ""

# if input_option == "✍️ Enter Text":
#     text_data = st.text_area("Enter text to translate:", height=200)

# elif input_option == "📂 Upload File":
#     uploaded_file = st.file_uploader("Upload a file (.pdf, .txt, .csv, .xlsx)", type=["pdf", "txt", "csv", "xlsx"])
#     if uploaded_file:
#         file_type = uploaded_file.name.split(".")[-1]
        
#         try:
#             if file_type == "pdf":
#                 reader = PyPDF2.PdfReader(uploaded_file)
#                 text_data = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
#             elif file_type == "txt":
#                 text_data = uploaded_file.read().decode("utf-8")
#             elif file_type == "csv":
#                 df = pd.read_csv(uploaded_file)
#                 text_data = df.to_string(index=False)
#             elif file_type == "xlsx":
#                 df = pd.read_excel(uploaded_file)
#                 text_data = df.to_string(index=False)
            
#             st.success(f"✅ Successfully extracted text from {uploaded_file.name}")
#             st.text_area("Extracted Text Preview:", text_data[:1000], height=200)
        
#         except Exception as e:
#             st.error(f"Error reading file: {e}")

# # --- LANGUAGE SELECTION ---
# languages = [
#     "English", "French", "Spanish", "German", "Italian",
#     "Hindi", "Chinese", "Japanese", "Korean", "Arabic", "Portuguese"
# ]

# st.subheader("🌍 Translation Settings")
# target_language = st.selectbox("Select Target Language:", languages)

# # Map full language names to gTTS language codes
# lang_codes = {
#     "English": "en",
#     "French": "fr",
#     "Spanish": "es",
#     "German": "de",
#     "Italian": "it",
#     "Hindi": "hi",
#     "Chinese": "zh-cn",
#     "Japanese": "ja",
#     "Korean": "ko",
#     "Arabic": "ar",
#     "Portuguese": "pt"
# }

# # --- TRANSLATION & TTS ---
# if st.button("Translate & Convert to Speech"):
#     if text_data and target_language:
#         with st.spinner("Translating text using GPT-3.5-turbo..."):
#             try:
#                 # Limit input length to avoid token overflow
#                 prompt = f"Translate the following text into {target_language}:\n\n{text_data[:2000]}"
                
#                 response = client.chat.completions.create(
#                     model="gpt-3.5-turbo",
#                     messages=[{"role": "user", "content": prompt}]
#                 )
#                 translated_text = response.choices[0].message.content.strip()

#                 st.success("✅ Translation Complete!")
#                 st.text_area("Translated Text:", translated_text, height=200)

#                 # --- SPEECH GENERATION FIX ---
#                 lang_code = lang_codes.get(target_language, "en")
#                 tts = gTTS(text=translated_text, lang=lang_code, slow=False)

#                 audio_fp = io.BytesIO()
#                 tts.write_to_fp(audio_fp)
#                 audio_fp.seek(0)

#                 # Playback and download
#                 st.audio(audio_fp, format="audio/mp3")
#                 st.download_button(
#                     label="⬇️ Download Audio",
#                     data=audio_fp,
#                     file_name=f"translated_{target_language}.mp3",
#                     mime="audio/mp3"
#                 )

#             except Exception as e:
#                 st.error(f"Translation or speech generation failed: {e}")
#     else:
#         st.warning("Please provide text or upload a file and select a language.")

import streamlit as st
from generate_code import OpenAI
from gtts import gTTS
import io
import os
import pandas as pd
import PyPDF2

# --------------------------
# 🔐 Set up OpenAI API key
# --------------------------
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"))

# --------------------------
# 🌐 Supported Languages
# --------------------------
languages = [
    "English", "French", "Spanish", "German", "Italian",
    "Hindi", "Chinese", "Japanese", "Korean", "Arabic", "Portuguese"
]

lang_codes = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Hindi": "hi",
    "Chinese": "zh-cn",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Portuguese": "pt"
}

# --------------------------
# 🧠 Translation Function
# --------------------------
# 🧠 Translation Function (Updated for OpenAI v1.x)
def translate_text(text, target_language):
    try:
        prompt = f"Translate the following text into {target_language}:\n\n{text}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Translation failed: {e}")
        return None

# --------------------------
# 🔉 Text-to-Speech Function
# --------------------------
def text_to_speech(text, language_name):
    try:
        lang_code = lang_codes.get(language_name, "en")
        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    except Exception as e:
        st.error(f"Speech generation failed: {e}")
        return None

# --------------------------
# 📄 File Text Extraction
# --------------------------
def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()

    try:
        if file_type == "txt":
            return uploaded_file.read().decode("utf-8")

        elif file_type == "pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text

        elif file_type in ["csv", "xlsx"]:
            if file_type == "csv":
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            return df.to_string(index=False)

        else:
            st.error("Unsupported file format. Please upload TXT, PDF, CSV, or Excel.")
            return None

    except Exception as e:
        st.error(f"File processing error: {e}")
        return None

# --------------------------
# 🎨 Streamlit UI Layout
# --------------------------
st.set_page_config(page_title="🌍 AI Translator & Speaker", layout="centered")
st.title("🌍 AI Translator & Speaker")
st.write("Translate text into multiple languages and generate speech using GPT-3.5 & gTTS.")

# --------------------------
# 📥 User Input Section
# --------------------------
input_method = st.radio("Choose Input Method:", ["Enter Text", "Upload File"])

user_text = ""

if input_method == "Enter Text":
    user_text = st.text_area("Enter text to translate:", height=200)

elif input_method == "Upload File":
    uploaded_file = st.file_uploader("Upload a file (TXT, PDF, CSV, Excel):", type=["txt", "pdf", "csv", "xlsx"])
    if uploaded_file:
        extracted_text = extract_text_from_file(uploaded_file)
        if extracted_text:
            st.success("File text extracted successfully!")
            user_text = extracted_text
            st.text_area("Extracted Text Preview:", user_text, height=200)

# --------------------------
# 🌎 Language Selection
# --------------------------
target_language = st.selectbox("Select Target Language:", languages)

# --------------------------
# 🚀 Translate & Speak
# --------------------------
if st.button("Translate & Generate Speech"):
    if not user_text.strip():
        st.warning("Please enter or upload text before proceeding.")
    else:
        with st.spinner("Translating... Please wait."):
            translated_text = translate_text(user_text, target_language)

        if translated_text:
            st.success("✅ Translation Complete!")
            st.subheader(f"Translated Text ({target_language}):")
            st.write(translated_text)

            with st.spinner("Generating speech..."):
                audio_fp = text_to_speech(translated_text, target_language)

            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")
                st.download_button(
                    label="⬇️ Download Audio File",
                    data=audio_fp,
                    file_name=f"translated_{target_language}.mp3",
                    mime="audio/mp3"
                )

# --------------------------
# 📘 Footer
# --------------------------
st.markdown("---")
st.caption("Developed as a Capstone Project using Streamlit, OpenAI GPT-3.5, and Google Text-to-Speech.")





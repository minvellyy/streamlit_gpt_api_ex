####### lib 설치 ##########
# pip install openai
# pip install streamlit
# pip install python-dotenv
# pip install moviepy
###########################
# 업로드 파일크기 25M 이하일 경우 
# 실행 : streamlit run 4-1.extraction_video.py
###########################

import streamlit as st
import os
import openai
from dotenv import load_dotenv
from moviepy import VideoFileClip

def extract_audio(video_path, audio_path):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, codec='mp3')

def transcribe_audio(audio_path, client):
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text

def save_file(content, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

# main 로직
def main():
    load_dotenv(override=True)
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    st.title("🎥 Video to Audio & Script Extractor")
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])
    
    if uploaded_file is not None:
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)

        video_path = os.path.join(temp_dir, uploaded_file.name)
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        audio_path = os.path.join(temp_dir, "extracted_audio.mp3")
        script_path = os.path.join(temp_dir, "transcribed_script.txt")

        st.info("Extracting audio...")
        extract_audio(video_path, audio_path)
        
        st.success("Audio extracted successfully! 🎵")
        
        st.info("Transcribing audio...")
        script_text = transcribe_audio(audio_path, client)
        save_file(script_text, script_path)
        
        st.success("Transcription completed! 📝")
        
        st.audio(audio_path, format='audio/mp3')
        
        st.subheader("Transcribed Script")
        st.text_area("", script_text, height=300)
        
        st.download_button("Download Audio", audio_path, file_name="extracted_audio.mp3")
        st.download_button("Download Script", script_path, file_name="transcribed_script.txt")
        
if __name__ == "__main__":
    main()
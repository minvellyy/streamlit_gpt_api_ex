####### lib 설치 ##########
# pip install openai
# pip install streamlit
# pip install python-dotenv
# pip install moviepy
###########################
# 업로드 파일크기 25M 이하일 경우 
# 실행 : streamlit run 4-1.extraction_video.py
###########################

# 모듈 불러오기
import streamlit as st
import os
import openai
from dotenv import load_dotenv
from moviepy import VideoFileClip  # 영상파일을 열어서 오디오 추출에 사용

# 영상 경로, 오디오 저장 경로
def extract_audio(video_path, audio_path):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, codec='mp3')  # 오디오 부분만 mp3로 저장

# 음성 -> 텍스트 변환 함수
def transcribe_audio(audio_path, client):
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text

# 타임스탬프 정보 가져오기
def transcribe_audio_with_timestamps(audio_path, client):
    """타임스탬프 포함 전사 함수"""
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["segment"]
        )
    return transcript

# 초 단위 숫자를 사람이 읽기쉬운 HH:MM:SS 형식으로 변환
def format_timestamp(seconds):
    """초를 HH:MM:SS 형식으로 변환"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

# 타임스탬프가 포함된 전사 데이터를 읽기 쉬운 형식으로 변환
def format_transcript_with_timestamps(transcript_data):
    formatted_text = ""
    
    for segment in transcript_data.segments:
        start_time = format_timestamp(segment.start)
        end_time = format_timestamp(segment.end)
        text = segment.text.strip()
        
        formatted_text += f"[{start_time} --> {end_time}]\n{text}\n\n"
    
    return formatted_text

def save_file(content, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


# 텍스트 파일 저장 함수
def save_file(content, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

# main 함수
def main():
    load_dotenv(override=True)
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # streamlit ui 파일 업로드
    st.title("🎥 Video to Audio & Script Extractor")

 # 타임스탬프 포함 여부 선택
    include_timestamps = st.checkbox("Include timestamps in transcription", value=False)
    
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])
    
    # 업로드 된 경우만 처리
    if uploaded_file is not None:
        #  임시 폴더 만들기 업로드 파일 저장
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
        
        # 다중 형식 출력
        st.subheader("Export summary / transcript")

        export_type = st.selectbox( # selectbox로 형식을 고를 수 있음
            "Choose export format",
            ["Text (.txt)", "Markdown (.md)", "CSV (.csv)"]
        )

        if st.button("Download Export File"):
            if export_type == "Text (.txt)":
                st.download_button(
                    "Download TXT",
                    data=script_text,  # 데이터를 파일 경로가 아닌 메모리 안의 텍스트를 바로 내려줌
                    file_name="transcript.txt",
                    mime="text/plain"
                )
            elif export_type == "Markdown (.md)":
                md_content = f"# Transcript\n\n{script_text}"
                st.download_button(
                    "Download MD",
                    data=md_content,
                    file_name="transcript.md",
                    mime="text/markdown"
                )
            elif export_type == "CSV (.csv)":
                csv_content = 'timestamp,text\n0:00:00,"' + script_text.replace('"', '""') + '"'
                st.download_button(
                    "Download CSV",
                    data=csv_content,
                    file_name="transcript.csv",
                    mime="text/csv"
                )
        # ==== 추가 끝 ====
        
 # 타임스탬프 포함 여부에 따라 다른 함수 호출
        if include_timestamps:
            transcript_data = transcribe_audio_with_timestamps(audio_path, client)
            script_text = format_transcript_with_timestamps(transcript_data)
        else:
            script_text = transcribe_audio(audio_path, client)

        save_file(script_text, script_path)
        
        st.success("Transcription completed! 📝")
        
        st.audio(audio_path, format='audio/mp3')
        
        st.subheader("Transcribed Script")
        st.text_area("", script_text, height=300)
        
        with open(audio_path, 'rb') as audio_file:
            st.download_button(
                "Download Audio", 
                audio_file.read(), 
                file_name="extracted_audio.mp3",
                mime="audio/mp3"
            )

        st.download_button(
            "Download Script", 
            script_text, 
            file_name="transcribed_script.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
    
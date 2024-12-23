import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai

# Set your OpenAI API key
openai.api_key = 'your-openai-api-key'

def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

def generate_learning_materials(transcript):
    # Use OpenAI to generate enriched content and questions
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Generate enriched content and multiple-choice questions from the following transcript: {transcript}",
        max_tokens=1500
    )
    return response.choices[0].text.strip()

def main():
    st.title("YouTube Learning Material Generator")

    # Input for YouTube link
    youtube_url = st.text_input("Enter YouTube URL:")

    if st.button("Submit"):
        if youtube_url:
            video_id = youtube_url.split("v=")[-1]
            transcript = get_youtube_transcript(video_id)
            if transcript:
                st.write("Transcript fetched successfully.")
                learning_materials = generate_learning_materials(transcript)
                st.write(learning_materials)
        else:
            st.error("Please enter a valid YouTube URL.")

if __name__ == "__main__":
    main() 
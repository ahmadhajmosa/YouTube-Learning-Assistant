"""
app.py
"""
import os

import streamlit as st
from openai import OpenAI
from openai.types.beta.thread_create_params import CodeInterpreterToolParam
from utils import (
    delete_files,
    delete_thread,
    EventHandler,
    initialise_session_state,
    moderation_endpoint,
    render_custom_css,
    render_download_files,
    retrieve_messages_from_thread,
    retrieve_assistant_created_files
    )

# Get secrets
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", st.secrets["OPENAI_API_KEY"])
ASSISTANT_ID = os.environ.get("OPENAI_ASSISTANT_ID", st.secrets["OPENAI_ASSISTANT_ID"])

print(ASSISTANT_ID)
# Initialise the OpenAI client, and retrieve the assistant
client = OpenAI(api_key=OPENAI_API_KEY)
assistant = client.beta.assistants.retrieve(ASSISTANT_ID)

st.set_page_config(page_title="YL",
                   page_icon="👨‍🏫")

# Apply custom CSS
render_custom_css()

# Initialise session state variables
initialise_session_state()

# UI
st.subheader("🔮 YouTube Learning Material Generator")
file_upload_box = st.empty()
upload_btn = st.empty()
text_box = st.empty()
qn_btn = st.empty()
def handle_url_input(url):
    """Function to handle URL input"""
    # Assuming a function to handle URL input and return a file ID
    return "file_id"
# File Upload or URL
if not st.session_state["file_uploaded"]:
    st.session_state["files"] = file_upload_box.file_uploader("Please upload your learning file(s) or enter a URL",
                                                              accept_multiple_files=True,
                                                              type=["pdf", "docx", "txt", "pptx", "ppt", "doc", "xlsx", "xls", "csv"])
    st.session_state["url"] = st.text_input("Or enter a URL to your learning material")

    if upload_btn.button("Upload") or (st.session_state["url"] and upload_btn.button("Submit URL")):

        st.session_state["file_id"] = []

        # Upload the file(s)
        if st.session_state["files"]:
            for file in st.session_state["files"]:
                oai_file = client.files.create(
                    file=file,
                    purpose='assistants'
                )
                # Append the file ID to the list
                st.session_state["file_id"].append(oai_file.id)
                print(f"Uploaded new file: \t {oai_file.id}")

        # Handle URL submission
        if st.session_state["url"]:
            # Assuming a function to handle URL input and return a file ID
            url_file_id = handle_url_input(st.session_state["url"])
            st.session_state["file_id"].append(url_file_id)
            print(f"Processed URL to file ID: \t {url_file_id}")

        st.toast("File(s) or URL processed successfully", icon="🚀")
        st.session_state["file_uploaded"] = True
        file_upload_box.empty()
        upload_btn.empty()
        # The re-run is to trigger the next section of the code
        st.rerun()

if st.session_state["file_uploaded"]:
    
    question = text_box.text_area("Ask a question")

    # If the button is clicked
    if qn_btn.button("Ask DAVE"):

        # Clear the UI
        text_box.empty()
        qn_btn.empty()

        # Check if the question is flagged
        if moderation_endpoint(question):
            # if flagged, return a warning message, delete the files and stop the app
            st.warning("Your question has been flagged. Refresh page to try again.")
            delete_files(st.session_state.file_id)
            st.stop()

        # If there is no text boxes in the session state, create an empty list 
        # This list will store the text boxes created by the Assistant
        if "text_boxes" not in st.session_state:
            st.session_state.text_boxes = []

        # Create a new thread if not already created
        if "thread_id" not in st.session_state:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id
            print(f"Created new thread: \t {st.session_state.thread_id}")
        for file_id in st.session_state.file_id:
            print(f"File ID: \t {file_id}")

        # Update the thread to attach the file(s)
        client.beta.threads.update(
            thread_id=st.session_state.thread_id
            )
        
        files = [file_id for file_id in st.session_state.file_id]

        # Ask the question
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=question,
            attachments = [
                {"file_id": files[0], "tools": [{"type": "file_search"}]}
            ]
              
        )
        

        # Create a new text box to display the question
        st.session_state.text_boxes.append(st.empty())
        st.session_state.text_boxes[-1].success(f"**> 🤔 User:** {question}")

        # Run the Assistant and the EventHandler handles the stream
        with client.beta.threads.runs.stream(thread_id=st.session_state.thread_id,
                                             assistant_id=assistant.id,
                                             tool_choice={"type": "file_search"},
                                             event_handler=EventHandler(),
                                             temperature=0) as stream:
            stream.until_done()
            st.toast("DAVE has finished analysing the data", icon="🕵️")

        # Prepare the files for download
        with st.spinner("Preparing the files for download..."):
            # Retrieve the messages by the Assistant from the thread
            assistant_messages = retrieve_messages_from_thread(st.session_state.thread_id)
            # For each assistant message, retrieve the file(s) created by the Assistant
            st.session_state.assistant_created_file_ids = retrieve_assistant_created_files(assistant_messages)
            # Download these files
            st.session_state.download_files, st.session_state.download_file_names = render_download_files(st.session_state.assistant_created_file_ids)

        # Clean-up
        # Delete the file(s) uploaded
        delete_files(st.session_state.file_id)
        # Delete the file(s) created by the Assistant
        delete_files(st.session_state.assistant_created_file_ids)
        # Delete the thread
        delete_thread(st.session_state.thread_id)
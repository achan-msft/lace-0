import streamlit as st
import os 
from openai import AzureOpenAI
from dotenv import load_dotenv
from converse import Converse 
from function.azure_storage import AzureStorage  

load_dotenv()
st.title("LACE")

# Set OpenAI API key from Streamlit secrets
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

client = AzureOpenAI(
    azure_endpoint = AZURE_OPENAI_ENDPOINT, 
    api_key = AZURE_OPENAI_API_KEY,  
    api_version = AZURE_OPENAI_API_VERSION
)

def show_loan_doc_uploader():
    show = True if "action" in st.session_state  and st.session_state["action"] == "apply_loan" else False 
    st.session_state["action"] = ""
    return show 

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"
if 'show_uploader' not in st.session_state:
    st.session_state['show_uploader'] = False   

converse = Converse()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state['show_uploader'] = False
    system_message = converse.get_init_system_message()
    st.session_state.messages = [system_message]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if "role" in message and message['role'] in ('assistant', 'user'):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

#----------------------------------------------------------------------------------------------------------------------------------
#   Accept user input
#----------------------------------------------------------------------------------------------------------------------------------
if prompt := st.chat_input():    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):        
        message = converse.start(message_list=st.session_state.messages, is_stream=True, streamlit=st)
        st.markdown(message)

        if show_loan_doc_uploader():
            st.session_state['show_uploader'] = True 

    st.session_state.messages.append({"role": "assistant", "content": message})

#----------------------------------------------------------------------------------------------------------------------------------
#   File upload
#----------------------------------------------------------------------------------------------------------------------------------
if st.session_state['show_uploader']:
    uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
    if uploaded_files is not None:
        # container_name = st.session_state["container_name"]
        folder_name = st.session_state["folder_name"]
        storage = AzureStorage() 

        st.session_state['all_uploaded'] = False
        files_count = 0 
        for file in uploaded_files:
            bytes_data = file.getvalue()
            # container = "06dece9a-199f-40a3-a3bc-b2b0fb11fa3f"
            file_name = f"{folder_name}/{file.name}"
            storage.upload(container=AZURE_STORAGE_CONTAINER_NAME, file_name=file_name, bytes=bytes_data)

            st.session_state['show_uploader'] = False 
            st.session_state['all_uploaded'] = True
            files_count += 1

        if st.session_state['all_uploaded']:
            st.success(f"{files_count} file(s) successfully uploaded")
            st.session_state['show_uploader'] = False

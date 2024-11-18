import streamlit as st
import os 
from openai import AzureOpenAI
from dotenv import load_dotenv
from converse import Converse 
from function import AzureStorage 

load_dotenv()
st.title("LACE")

# Set OpenAI API key from Streamlit secrets
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# client = OpenAI(api_key=AZURE_OPENAI_API_KEY)
client = AzureOpenAI(
    azure_endpoint = AZURE_OPENAI_ENDPOINT, 
    api_key = AZURE_OPENAI_API_KEY,  
    api_version = AZURE_OPENAI_API_VERSION
)
# client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


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
#   file upload 
#----------------------------------------------------------------------------------------------------------------------------------
# if "show_uploader" in st.session_state and st.session_state['show_uploader']:      
#     # If the file was uploaded, you can prompt the user for further actions         
#     st.write("You have successfully uploaded a file. How can I assist you next?")   
#     st.session_state['show_uploader'] = False 

#     st.chat_input("What is up?")

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

        if 'name' in st.session_state.messages[-1] and st.session_state.messages[-1]['name'] == 'apply_loan':
            st.session_state['show_uploader'] = True 

    st.session_state.messages.append({"role": "assistant", "content": message})

#   file upload
if st.session_state['show_uploader']:

    uploaded_file = st.file_uploader("Upload a file", type=["txt", "csv"])
    if uploaded_file:
        container_name = st.session_state["container_name"]
        # bytes_data = uploaded_file.getvalue() 
        # st.write(bytes_data)

        storage = AzureStorage()            
        _, sas_url = storage.upload_file_to_azure_container(container_name)



        st.success("file succwessfully uploaded")
        st.session_state['show_uploader'] = False 


# uploaded_file = st.file_uploader("Upload your file")
# if uploaded_file is not None:
    # Perform file validation and processing here
    # st.success("File successfully uploaded!")

import streamlit as st
import pandas as pd
from io import StringIO
from function.azure_storage import AzureStorage  

uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
if uploaded_files is not None:
    # To read file as bytes:

    for file in uploaded_files:
        bytes_data = file.getvalue()
        storage = AzureStorage() 
        container = "06dece9a-199f-40a3-a3bc-b2b0fb11fa3f"
        storage.upload(container=container, file_name=file.name, bytes=bytes_data)
    
    # bytes_data = uploaded_file.getvalue()
    # storage = AzureStorage() 
    # container = "06dece9a-199f-40a3-a3bc-b2b0fb11fa3f"
    # file_name= "sdaf"
    # storage.upload(container=container, file_name=uploaded_file.name, bytes=bytes_data)
    asdff = "dsaf"
    
    # st.success("file succwessfully uploaded")
# container, file_name, bytes)

    # Can be used wherever a "file-like" object is accepted:
    # dataframe = pd.read_csv(uploaded_file)
    # st.write(dataframe)


# import streamlit as st

# # Initialize a session state variable to track the chatbot state
# if 'file_uploaded' not in st.session_state:
#     st.session_state.file_uploaded = False

# # Display the chatbot's instructions or greeting
# st.write("Hello! How can I assist you today? Type 'upload file' to upload a file.")

# # User input field for chatbot conversation
# user_input = st.text_input("You: ")

# # Check if the user's input matches the intent "upload file"
# if user_input.lower() == "upload file":
#     # Show the file uploader widget if the user wants to upload a file
#     uploaded_file = st.file_uploader("Choose a file", type=["csv", "txt", "pdf", "xlsx"])
    
#     if uploaded_file is not None:
#         # If a file is uploaded, process it and set a flag to indicate that the file was uploaded
#         st.session_state.file_uploaded = True
#         st.write(f"File uploaded: {uploaded_file.name}")
        
#         # Now you can process the file as needed, for example:
#         # If the file is a CSV, you could read it using pandas (if the file is a CSV)
#         if uploaded_file.name.endswith('.csv'):
#             import pandas as pd
#             df = pd.read_csv(uploaded_file)
#             st.write(df.head())  # Display the first few rows of the uploaded CSV
#         # Add processing logic for other file types here if needed

# elif st.session_state.file_uploaded:
#     # If the file was uploaded, you can prompt the user for further actions
#     st.write("You have successfully uploaded a file. How can I assist you next?")
# else:
#     # If the user hasn't requested file upload, continue the conversation
#     if user_input:
#         st.write(f"Bot: You said: {user_input}")

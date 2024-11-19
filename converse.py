from openai import AzureOpenAI 
import json, jsonref, os, uuid 
from function.azure_storage import AzureStorage  
from function.utility_datetime import DateTimeUtility
from function.database.loan_application import LoanApplication 
import streamlit

class Converse():
    def __init__(self, *args, **kwds):
        self.AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
        self.AZURE_OPENAI_DEPLOYMENT_NAME =  os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") # "gpt-4o" # os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME') # "gpt-4o" #os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION") # "2024-08-01-preview" # os.getenv("AZURE_OPENAI_API_VERSION") # os.environ["AZURE_OPENAI_API_VERSION"]
        self.TOOLS_FILE_NAME = "tools.json"

        # system_content ="You are a helpful assistant. Respond concisely and clearly. if someone asks for the current place, reply i don't know."
        # system_message = { "role": "system", "content": system_content }

        # self.system_message = system_message        
        self.tools = self.get_tools_content()  

    def get_init_system_message(self):
        system_content ="Hello I'm an AI assistant. I can help you with the loan processing."
        system_message = { "role": "assistant", "content": system_content }

        return system_message 
    
    def start(self, message_list, is_stream, streamlit):
        # user_message = { "role": "user", "content": user_message_content } 
        # messages = [self.system_message, user_message] # Parallel function call with a single tool/function defined

        client = AzureOpenAI(
            azure_endpoint = self.AZURE_OPENAI_ENDPOINT, 
            api_key = self.AZURE_OPENAI_API_KEY,  
            api_version = self.AZURE_OPENAI_API_VERSION
        )

        # First API call: Ask the model to use the function
        response = client.chat.completions.create(
            model=self.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=message_list,
            tools=self.tools,
            tool_choice="auto",
            stream=False,
        )

        # stream = client.chat.completions.create(
        #     model=self.AZURE_OPENAI_DEPLOYMENT_NAME,
        #     messages=[
        #         {"role": m["role"], "content": m["content"]}
        #         for m in st.session_state.messages
        #     ],
        #     stream=True,
        # )

        # Process the model's response
        response_message = response.choices[0].message
        
        # if response_message.tool_calls is not None:
        message_list.append(response_message)
        # messages.append(response_message)

        # Handle function calls
        # if response_message.tool_calls:
        #     for tool_call in response_message.tool_calls:
        #         self.process_message(tool_call, message_list)
  
        if response_message.tool_calls: # self.need_extra_call(messages):
            for tool_call in response_message.tool_calls:
                self.process_message(tool_call, message_list, streamlit)

            # Second API call: Get the final response from the model
            final_response = client.chat.completions.create(
                model=self.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=message_list,
            )
            final_message = final_response.choices[0].message.content
        
        else:
            final_message = message_list[-1].content
            
        return final_message # final_response.choices[0].message.content

    def process_message(self, tool_call, messages: list, st: streamlit):
        if tool_call.function.name == "get_current_time":
            function_args = json.loads(tool_call.function.arguments)
            time_response = DateTimeUtility.get_current_time(
                location=function_args.get("location")
            )
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_call.function.name,
                "content": time_response,
            })

        elif tool_call.function.name == "create_azure_container":
            function_args = json.loads(tool_call.function.arguments)
            # print(f"Function arguments: {function_args}")  
            storage = AzureStorage()            
            _, sas_url = storage.create_azure_container_and_sas_url(
                container_name=function_args.get("container_name")
            )

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_call.function.name,
                "content": f'Please upload your documents at this url:{sas_url}',
            })

        elif tool_call.function.name == "apply_loan":
            function_args = json.loads(tool_call.function.arguments)
            storage = AzureStorage()       

            if "folder_name" in st.session_state and st.session_state["folder_name"] != "":     
                folder_name = st.session_state["folder_name"]
            else:
                folder_name = str(uuid.uuid4()) # function_args.get("container_name")
                st.session_state["folder_name"] = folder_name 

            data = {
                "folder_name": folder_name
            }
            la = LoanApplication()
            record = la.insert_loan_application(data)

            content = f"Your application id is {record["id"]}.  Please upload your documents"
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_call.function.name,
                "content": content
            })

        elif tool_call.function.name == "get_loan_status":
            # working in progress
            if tool_call.function.arguments is None or "loan" not in tool_call.function.arguments:
                return  
            
            function_args = json.loads(tool_call.function.arguments)
            la = LoanApplication()
            record = la.get_loan_application(loan_application_id=function_args.get("loan_id"))

            # content = f"The status id is {record["id"]}."
            content = f"The loan status is {record['status']}." 

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_call.function.name,
                "content": content
            })

    def get_tools_content(self):
        try: 
            with open(self.TOOLS_FILE_NAME, 'r') as f:
                content = f.read()
                tools = jsonref.loads(content)
                return tools 

        except Exception as e:
            print(e)

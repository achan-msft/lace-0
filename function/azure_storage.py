import os 
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, generate_container_sas, ContainerSasPermissions
from datetime import datetime, timedelta
from dotenv import load_dotenv


class AzureStorage:    
    def __init__(self):
        try:
            load_dotenv()
            self.STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME") # "llmstorage1"
            self.account_url = f"https://{self.STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
            self.credential = DefaultAzureCredential()

        except Exception as e:
            print(f"exception within constructor:{e}")

    def create_azure_container_and_sas_url(self, container_name):
        successful = self.create_container(container_name) 
        sas_url = self.get_sas_url(container_name)
        
        return successful, sas_url 

    def create_container(self, container_name):
        try:
            blob_service_client = BlobServiceClient(self.account_url, credential=self.credential)      
            blob_service_client.create_container(container_name)
            return True
        
        except ResourceExistsError:  # already existed 
            return False

        except Exception as e:
            print(e)
            return False

    def get_sas_url(self, container_name):
        try:
            key_start_time = datetime.utcnow()  # - timedelta(hours=.1) 
            key_expiry_time = datetime.utcnow() + timedelta(hours=10)     
            blob_service_client = BlobServiceClient(self.account_url, credential=self.credential) 
            user_delegation_key = blob_service_client.get_user_delegation_key(key_start_time, key_expiry_time)

            permission = ContainerSasPermissions(read=True, write=True, delete=True, create=True, delete_previous_version=True, move=True, list=True, add=True, update=True, process=True)
            sas = generate_container_sas(expiry=key_expiry_time, account_name=self.STORAGE_ACCOUNT_NAME, container_name=container_name, user_delegation_key=user_delegation_key, permission=permission)
            sas_url = f"{self.account_url}/{container_name}?{sas}"
            
            return sas_url
        
        except Exception as e: 
            print(e)    

    def upload(self, container, file_name, bytes):        
        try:
            blob_service_client = BlobServiceClient(self.account_url, credential=self.credential)                  
            blob_client = blob_service_client.get_blob_client(container=container, blob=file_name)
            blob_client.upload_blob(bytes)

        except Exception as e:
            print(e)
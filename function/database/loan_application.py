import os 
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

# for LocalAuthentication issue, execute the follwoing 
# az resource update --resource-group "harrchen-rg" --name "harrchencosmos1" 
# --resource-type "Microsoft.DocumentDB/databaseAccounts" 
# --set properties.disableLocalAuth=false

class LoanApplication:
    def __init__(self):            
        try:
            # Set up Cosmos DB        
            COSMOS_ENDPOINT = os.getenv('COSMOS_ENDPOINT')
            COSMOS_KEY = os.getenv('COSMOS_KEY')
            COSMOS_DATABASE = os.getenv('COSMOS_DATABASE') 
            COSMOS_LOAN_APPLICATION_CONTAINER = os.getenv("COSMOS_LOAN_APPLICATION_CONTAINER")
            COSMOS_LOAN_CONTAINER = os.getenv("COSMOS_LOAN_CONTAINER")

            # credential = DefaultAzureCredential()
            # self.client = CosmosClient(COSMOS_ENDPOINT, credential)
            self.client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
            self.database = self.client.get_database_client(COSMOS_DATABASE)
            self.loan_application_container = self.database.get_container_client(COSMOS_LOAN_APPLICATION_CONTAINER)
            self.loan_container = self.database.get_container_client(COSMOS_LOAN_CONTAINER)

        except Exception as e:
            print(e)

    def get_latest_loan_application_id(self):
        loan_application_id = 0
        query = "SELECT VALUE MAX(StringToNumber(c.id)) FROM c"
        
        try:
            items = list(self.loan_application_container.query_items(query=query, enable_cross_partition_query=True))        
            loan_application_id = 1 if items[0] is None else int(items[0]) + 1
        
        except Exception as e:
            print(e)

        return loan_application_id
    
    def insert_loan_application(self, application_data: dict):        
        try:
            application_data["id"] = str(self.get_latest_loan_application_id())

            record = self.loan_application_container.upsert_item(body=application_data)
            return record

        except Exception as e:
            print(e)

    # TODO item
    def delete(self):
        query = "SELECT * FROM c"
        try: 
            for item in self.container.query_items(query=query, enable_cross_partition_query=True):
                self.container.delete_item(item, partition_key=item['id']) 
                # self.container.delete_all_items_by_partition_key(item['id'])
                # self.container.replace_item(item=item, id=item['id'], partition_key="1", body=item)

                # self.container.delete_item()
                # response = self.container.delete_item(item=item, partition_key='')
                asdfs="sadf"


        except Exception as e: 
            print(e)

    def get_loan_application(self, loan_application_id):
        query = "SELECT * FROM c"
        query = f"SELECT * FROM c WHERE c.id = '{loan_application_id}'"
        items = list(self.loan_container.query_items(query=query, enable_cross_partition_query=True))
        return items[0] if items else []

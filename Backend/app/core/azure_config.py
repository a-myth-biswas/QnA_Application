from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

class AzureConfig:
    def __init__(self):
        self.OPENAI_API_TYPE=os.getenv('OPENAI_API_TYPE')
        self.OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')
        self.AZURE_ENDPOINT=os.getenv('AZURE_ENDPOINT')
        self.OPENAI_API_VERSION=os.getenv('OPENAI_API_VERSION')
    

    def llm_initialize(self):
        llm = AzureChatOpenAI(
            temperature=0.2,
            model="gpt-4o",
            deployment_name="gpt-4o",
            openai_api_key=self.OPENAI_API_KEY,
            openai_api_version=self.OPENAI_API_VERSION,
            azure_endpoint=self.AZURE_ENDPOINT,
            openai_api_type=self.OPENAI_API_TYPE,
        )
        return llm
    

    def embedding_initialize(self):
        azure_embedding = AzureOpenAIEmbeddings(
            model="text-embedding-3-small",       
            azure_deployment="embed3",          
            azure_endpoint=self.AZURE_ENDPOINT,  
            openai_api_key=self.OPENAI_API_KEY,           
            openai_api_version=self.OPENAI_API_VERSION,                             
            openai_api_type=self.OPENAI_API_TYPE,                                      
        )
        return azure_embedding
        


if __name__=="__main__":
    config = AzureConfig()
    llm = config.llm_initialize()
    azure_embedding = config.embedding_initialize()
    print(llm)
    print(azure_embedding)
    embed = azure_embedding.embed_query("what a beautifull day")
    print(embed)



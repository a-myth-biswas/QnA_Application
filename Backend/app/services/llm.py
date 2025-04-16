from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from langchain_core.output_parsers.json import SimpleJsonOutputParser
from langchain_core.output_parsers.string import StrOutputParser
from Backend.app.core.azure_config import AzureConfig
from Backend.app.services.retriever import retrieve_documents
from Backend.app.services.reranker import rerank_documents

config = AzureConfig()
llm = config.llm_initialize()

template_gpt = """
You are a professional document analyst. Use the following context to answer questions.
Your answers must be:
- Based exclusively on the provided context
- Concise but comprehensive
- Formatted in natural human-readable English
- Cite document sources when available
---------------------------
Context : {context},
---------------------------
Question : {query},
---------------------------
Response :
"""

prompt_gpt = PromptTemplate(
    input_variables=["context", "query"],
    template=template_gpt,
)


# Function to get the final response
def get_final_response(query, document_id):
    # Retrieve documents along with metadata (document_id, filename, upload_time)
    db_path = "./ChromaDB"
    print("doc id in LLM", document_id)
    retrieved_docs = retrieve_documents(query, db_path, filter_document_id=document_id)
    print("document retrived successfully")
    # Rank the documents by relevance to the query
    top_docs = rerank_documents(query, retrieved_docs, k=3)
    print("reranked successfully", top_docs)
    # Prepare the context for GPT, including document metadata (document_id, filename, upload_time)
    context = "\n\n".join([f"Document ID: {doc.metadata['document_id']}, "
                           f"Filename: {doc.metadata['filename']}, "
                           # f"Upload Time: {doc.metadata['upload_time']}, "
                           f"Content: {doc.page_content}" for doc in top_docs])

    # Initialize output parsers
    json_parser = SimpleJsonOutputParser()
    str_parser = StrOutputParser()

    # Chain the prompt, LLM, and parser together
    chain = prompt_gpt | llm | str_parser

    # Get the response from the chain
    response = chain.invoke({"context": context, "query": query})

    return response


# from langchain_core.prompts import PromptTemplate
# from langchain.schema.runnable import RunnableSequence
# from langchain_core.output_parsers.json import SimpleJsonOutputParser
# from langchain_core.output_parsers.string import StrOutputParser
# from app.core.azure_config import AzureConfig
# from app.services.retriever import retrieve_documents
# from app.services.reranker import rerank_documents
# config = AzureConfig()
# llm = config.llm_initialize()
#
# template_gpt = """
# You are a professional document analyst. Use the following context to answer questions.
# Your answers must be:
# - Based exclusively on the provided context
# - Concise but comprehensive
# - Formatted in natural human-readable English
# - Cite document sources when available
# ---------------------------
# Context : {context},
# ---------------------------
# Question : {query},
# ---------------------------
# Response :
# """
#
# prompt_gpt = PromptTemplate(
#     input_variables=["context", "query"],
#     template=template_gpt,
# )
#
#
# # Function to get the final response
# def get_final_response(query, uuid_path):
#     # Combine the documents' text into the context for the prompt
#     retrieved_docs = retrieve_documents(query, uuid_path)
#     top_docs = rerank_documents(query, retrieved_docs, k=3)
#     context = "\n\n".join([doc.page_content for doc in top_docs])
#     json_parser = SimpleJsonOutputParser()
#     str_parser = StrOutputParser()
#     chain = prompt_gpt | llm | str_parser
#     response = chain.invoke({"context": context, "query": query})
#     # Create the RunnableSequence to combine the prompt and the LLM
#     # qa_sequence = RunnableSequence([prompt_gpt, llm])
#
#     # # Execute the sequence to generate the response
#     # response = qa_sequence.invoke({"context": context, "query": query})
#
#     return response

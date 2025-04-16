from db.db import db_creation
from services.chunking import *
from services.llm import get_final_response
_path = "/shared_disk/amitv/JKTech/Samples/CSR-POLICY.pdf"

docs = pdf_to_text(_path)
chunks = chunking(docs)
db_creation(chunks)
query="what is the contribution made by JK tech in during FY 2017-18"
response = get_final_response(query)
print(response)
import os
import pickle
import json
import numpy as np
import faiss
from langchain.schema import Document
from Backend.app.core.azure_config import AzureConfig
from datetime import datetime
import uuid

config = AzureConfig()
azure_embeddings = config.embedding_initialize()

def db_creation(docs, filename, doc_id=None, base_dir="./ChromaDB", batch_size=60):
    os.makedirs(base_dir, exist_ok=True)

    # File paths
    faiss_file = os.path.join(base_dir, "faiss_index_test.bin")
    docstore_file = os.path.join(base_dir, "docstore_final_test.pkl")
    mapping_file = os.path.join(base_dir, "index_to_docstore_id.json")
    metadata_file = os.path.join(base_dir, "metadata.json")

    # Load or initialize
    if os.path.exists(faiss_file):
        print("Appending to existing vector store...")
        faiss_index = faiss.read_index(faiss_file)
        with open(docstore_file, "rb") as f:
            docstore = pickle.load(f)
        with open(mapping_file, "r") as f:
            index_to_docstore_id = json.load(f)
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
    else:
        print("Creating new vector store...")
        embedding_dim = 1536
        faiss_index = faiss.IndexFlatL2(embedding_dim)
        docstore = {}
        index_to_docstore_id = {}
        metadata = {}

    current_max_id = max([int(k) for k in index_to_docstore_id.keys()], default=-1)
    doc_id_counter = current_max_id + 1

    document_id = doc_id or str(uuid.uuid4())
    upload_time = datetime.utcnow().isoformat()

    # Break into batches
    batches = [docs[i:i + batch_size] for i in range(0, len(docs), batch_size)]
    num_chunks = 0

    for batch in batches:
        embeddings_batch = [azure_embeddings.embed_query(doc.page_content) for doc in batch]
        embeddings_batch = np.vstack(embeddings_batch).astype("float32")
        faiss_index.add(embeddings_batch)
        for doc in batch:
            chunk_uuid = str(uuid.uuid4())  # Unique per chunk
            faiss_idx = str(len(index_to_docstore_id))  # FAISS index corresponds to order of addition

            docstore[chunk_uuid] = doc
            index_to_docstore_id[faiss_idx] = chunk_uuid
            metadata[chunk_uuid] = {
                "document_id": document_id,
                "filename": filename,
                "upload_time": upload_time,
                "chunk_index": num_chunks
            }
        # for doc in batch:
        #     docstore[str(doc_id_counter)] = doc
        #     index_to_docstore_id[str(doc_id_counter)] = document_id
        #     metadata[str(doc_id_counter)] = {
        #         "document_id": document_id,
        #         "filename": filename,
        #         "upload_time": upload_time,
        #         "chunk_index": num_chunks
        #     }
            doc_id_counter += 1
            num_chunks += 1

    # Save updated components
    faiss.write_index(faiss_index, faiss_file)
    with open(docstore_file, "wb") as f:
        pickle.dump(docstore, f)
    with open(mapping_file, "w") as f:
        json.dump(index_to_docstore_id, f, indent=2)
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Stored {num_chunks} chunks for file: {filename} with document_id: {document_id}")
    return document_id


# import os
# import pickle
# import json
# import numpy as np
# import faiss
# from langchain.schema import Document
# from app.core.azure_config import AzureConfig
#
# config = AzureConfig()
# azure_embeddings = config.embedding_initialize()
#
# def db_creation(docs, target_dir, batch_size=60):
#     db_path = target_dir
#     faiss_file = os.path.join(db_path, "faiss_index_test.bin")
#     docstore_file = os.path.join(db_path, "docstore_final_test.pkl")
#     mapping_file = os.path.join(db_path, "index_to_docstore_id.json")
#
#     os.makedirs(db_path, exist_ok=True)
#
#     # Check if files exist already
#     if os.path.exists(faiss_file) and os.path.exists(docstore_file) and os.path.exists(mapping_file):
#         print("Existing vector store found. Loading...")
#
#         faiss_index = faiss.read_index(faiss_file)
#
#         with open(docstore_file, "rb") as f:
#             docstore = pickle.load(f)
#
#         with open(mapping_file, "r") as f:
#             index_to_docstore_id = json.load(f)
#
#         print("Vector store loaded successfully.")
#         return faiss_index, docstore, index_to_docstore_id
#
#     print("No existing vector store found. Creating new FAISS index...")
#
#     # Create new FAISS index
#     embedding_dim = 1536
#     faiss_index = faiss.IndexFlatL2(embedding_dim)
#     docstore = {}
#     index_to_docstore_id = {}
#
#     # Break into batches
#     batches = [docs[i:i + batch_size] for i in range(0, len(docs), batch_size)]
#
#     for batch_idx, batch in enumerate(batches):
#         embeddings_batch = [azure_embeddings.embed_query(doc.page_content) for doc in batch]
#         embeddings_batch = np.vstack(embeddings_batch).astype("float32")
#         faiss_index.add(embeddings_batch)
#
#         for i, doc in enumerate(batch):
#             doc_id = batch_idx * batch_size + i
#             docstore[doc_id] = doc
#             index_to_docstore_id[doc_id] = doc_id
#
#     # Save everything
#     faiss.write_index(faiss_index, faiss_file)
#
#     with open(docstore_file, "wb") as f:
#         pickle.dump(docstore, f)
#
#     with open(mapping_file, "w") as f:
#         json.dump(index_to_docstore_id, f)
#
#     print("Vector store created and saved successfully.")
#     return faiss_index, docstore, index_to_docstore_id

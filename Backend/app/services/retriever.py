from Backend.app.core.azure_config import AzureConfig
from Backend.app.core.utils import load_resources
import numpy as np

config = AzureConfig()
azure_embeddings = config.embedding_initialize()


def retrieve_documents(query, db_path, filter_document_id=None, k=12):
    """Retrieve top-k documents for the query using Azure embeddings"""
    # Load FAISS index, docstore, mapping, and metadata
    docstore, faiss_index, index_to_docstore_id, metadata = load_resources(db_path)
    print(docstore, faiss_index, index_to_docstore_id, metadata)
    # Generate query embedding using Azure embeddings
    query_embedding = azure_embeddings.embed_query(query)

    # Convert query embedding to numpy float32 (required for FAISS)
    query_embedding = np.array(query_embedding, dtype="float32").reshape(1, -1)

    # Ensure the query embedding matches FAISS index dimensions
    if query_embedding.shape[1] != faiss_index.d:
        raise ValueError(f"Dimension mismatch: query embedding ({query_embedding.shape[1]}) "
                         f"and FAISS index ({faiss_index.d}) do not match.")

    # Perform similarity search in the FAISS index
    _, indices = faiss_index.search(query_embedding, k)  # Get top-k results

    # Retrieve document objects from the docstore
    retrieved_docs = []
    for idx in indices[0]:
        doc_id_str = str(idx)
        if doc_id_str in index_to_docstore_id:
            doc_id = index_to_docstore_id[doc_id_str]
            doc = docstore.get(str(doc_id))
            if doc:
                if filter_document_id:
                    # Check against metadata
                    chunk_meta = chunk_meta = metadata.get(doc_id, {})
                    if chunk_meta.get("document_id") != filter_document_id:
                        continue
                retrieved_docs.append(doc)

    if not retrieved_docs:
        print("No documents retrieved.")
    else:
        print(f"Retrieved {len(retrieved_docs)} documents.")

    return retrieved_docs  # Optionally return metadata alongside, if needed


# from app.core.azure_config import AzureConfig
# from app.core.utils import load_resources
# import numpy as np
#
# config = AzureConfig()
# azure_embeddings = config.embedding_initialize()
#
#
# def retrieve_documents(query, uuid_path, k=12):
#     """Retrieve top-k documents for the query using Azure embeddings"""
#     # Load resources
#     docstore, faiss_index, index_to_docstore_id = load_resources(uuid_path)
#
#     # Generate query embedding using Azure embeddings
#     query_embedding = azure_embeddings.embed_query(query)
#
#     # Convert query embedding to numpy float32 (required for FAISS)
#     query_embedding = np.array(query_embedding, dtype="float32").reshape(1, -1)
#
#     # Ensure the query embedding matches FAISS index dimensions
#     if query_embedding.shape[1] != faiss_index.d:
#         raise ValueError(f"Dimension mismatch: query embedding ({query_embedding.shape[1]}) "
#                          f"and FAISS index ({faiss_index.d}) do not match.")
#
#     # Perform similarity search in the FAISS index
#     _, indices = faiss_index.search(query_embedding, k)  # Get top-k results
#
#     # Retrieve document IDs from the indices and map them to docstore
#     retrieved_docs = []
#     for idx in indices[0]:
#         # Ensure index is valid
#         if str(idx) in index_to_docstore_id:
#             doc_id = index_to_docstore_id[str(idx)]
#             doc = docstore.get(doc_id, None)
#             if doc:
#                 retrieved_docs.append(doc)
#
#     if not retrieved_docs:
#         print("No documents retrieved.")
#     else:
#         print(f"Retrieved {len(retrieved_docs)} documents.")
#
#     return retrieved_docs

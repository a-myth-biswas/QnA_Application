import os
import pickle
import faiss
import json


def load_resources(db_path):
    """Load FAISS index, document store, index-to-docstore ID mapping, and metadata"""

    # Load FAISS index
    faiss_index_file = os.path.join(db_path, "faiss_index_test.bin")
    faiss_index = faiss.read_index(faiss_index_file)

    # Load docstore
    docstore_file = os.path.join(db_path, "docstore_final_test.pkl")
    with open(docstore_file, "rb") as f:
        docstore = pickle.load(f)

    # Load index-to-docstore ID mapping
    mapping_file = os.path.join(db_path, "index_to_docstore_id.json")
    with open(mapping_file, "r") as f:
        index_to_docstore_id = json.load(f)

    # Load metadata
    metadata_file = os.path.join(db_path, "metadata.json")
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
    else:
        metadata = {}

    return docstore, faiss_index, index_to_docstore_id, metadata


# import os
# import pickle
# import faiss
# import json
#
# def load_resources(_path):
#     """Load FAISS index, document store, and index-to-docstore ID mapping"""
#     # Load docstore (Document store containing the actual documents)
#     docstore_final_test = os.path.join(_path, 'docstore_final_test.pkl')
#     with open(docstore_final_test, 'rb') as f:
#         docstore = pickle.load(f)
#
#     # Load FAISS index
#     faiss_index_test = os.path.join(_path, "faiss_index_test.bin")
#     faiss_index = faiss.read_index(faiss_index_test)
#
#     # Load index to docstore id mapping
#     index_to_docstore_id_path = os.path.join(_path, 'index_to_docstore_id.json')
#     with open(index_to_docstore_id_path, 'r') as f:
#         index_to_docstore_id = json.load(f)
#
#     return docstore, faiss_index, index_to_docstore_id

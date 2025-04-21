import os
import pickle
import faiss
import json
from jose import jwt
import datetime


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


def create_access_token(SECRET_KEY, ALGORITHM, data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



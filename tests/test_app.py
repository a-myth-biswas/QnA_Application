import os
import json
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from Backend.app.api.app import app  # Adjust if your app file is named differently

UPLOAD_TRACKER_FILE = "uploaded_docs.json"
client = TestClient(app)


def test_upload_pdf():
    test_file_path = "/shared_disk/amitv/JKTech/tests/sample.pdf"
    # Ensure the sample PDF exists
    assert os.path.exists(test_file_path)

    with open(test_file_path, "rb") as f:
        files = {"file": ("sample.pdf", f, "application/pdf")}
        response = client.post("/upload_pdf", files=files)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "pdf_folder" in data
    assert "filename" in data
    assert data["filename"] == "sample.pdf"


def test_query_success():
    # Load document ID from the upload tracker
    if not os.path.exists(UPLOAD_TRACKER_FILE):
        pytest.skip("No document uploaded to test query.")
    with open(UPLOAD_TRACKER_FILE) as f:
        docs = json.load(f)
        if not docs:
            pytest.skip("No document data available.")
        folder = docs[-1]["path"]

    payload = {
        "query": "What is the content of the document?",
        "db_folder": folder
    }

    response = client.post("/query", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data


def test_query_empty_input():
    payload = {"query": " ", "db_folder": "fake_folder"}
    response = client.post("/query", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Query can not be empty"


def test_query_invalid_folder():
    payload = {"query": "test?", "db_folder": "invalid_path_123"}
    response = client.post("/query", json=payload)

    assert response.status_code == 404


def test_list_documents():
    response = client.get("/documents")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_upload_no_file():
    response = client.post("/upload_pdf", files={})
    assert response.status_code == 422
    assert "file" in response.json()["detail"][0]["loc"]



def test_upload_invalid_file():
    file_path = "/shared_disk/amitv/JKTech/tests/stlit.txt"
    with open(file_path, "rb") as f:
        response = client.post("/upload_pdf", files={"file": ("sample.txt", f, "text/plain")})
    assert response.status_code == 400
    assert "only pdf files are allowed" in response.json()["detail"].lower()



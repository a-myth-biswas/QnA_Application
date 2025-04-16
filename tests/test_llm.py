import pytest
from Backend.app.services.llm import get_final_response

def test_llm_with_mocked_docs(monkeypatch):
    # Step 1: Mock document object
    class MockDoc:
        def __init__(self):
            self.metadata = {
                "document_id": "doc1",
                "filename": "mocked_file.pdf"
            }
            self.page_content = "This is mocked content."

    mock_docs = [MockDoc()]

    # Step 2: Mock retriever function
    monkeypatch.setattr("app.services.retriever.retrieve_documents",
                        lambda query, db_path, filter_document_id: mock_docs)

    # Step 3: Mock reranker function — THIS IS CRUCIAL
    monkeypatch.setattr("app.services.reranker.rerank_documents",
                        lambda query, docs, k: docs)

    # Step 4: Mock the LLM chain — override the full chain's .invoke()
    class MockChain:
        def invoke(self, inputs):
            return "Mocked response from LLM."

    # Step 5: Patch the LLM chain
    from Backend.app.services import llm
    monkeypatch.setattr(llm.prompt_gpt, "__or__", lambda self, other: MockChain())

    # Step 6: Call your function
    response = get_final_response("What is in the document?", "doc1")

    assert isinstance(response, str)
    assert "mocked" in response.lower()

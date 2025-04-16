from sentence_transformers import SentenceTransformer, util
import torch


def rerank_documents(queries, documents, k=4):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    reranker_model = SentenceTransformer("BAAI/bge-large-en-v1.5", device=device)
    doc_texts = [doc.page_content for doc in documents]
    query_embedding = reranker_model.encode(queries, convert_to_tensor=True, device=device)
    doc_embeddings = reranker_model.encode(doc_texts, convert_to_tensor=True, device=device)
    similarities = util.cos_sim(query_embedding, doc_embeddings).squeeze(0)
    top_k_indices = similarities.argsort(descending=True)[:k]
    return [documents[i] for i in top_k_indices]

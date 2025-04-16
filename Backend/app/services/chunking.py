# chunking.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List, Union
import PyPDF2
import io
import os


def chunking(data: List[Document]) -> List[Document]:
    """Split documents into manageable chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1300,
        chunk_overlap=300,
        separators=["\n\n", "\n", " ", ""]  # Natural breaking points
    )
    return text_splitter.split_documents(data)


def pdf_to_text(pdf_path: str, document_id: str) -> List[Document]:
    """Convert PDF pages to text documents with metadata"""
    documents = []

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            for page_num, page in enumerate(pdf_reader.pages, start=1):
                text = page.extract_text()

                if text.strip():  # Skip empty pages
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "document_id": document_id,  # Add document_id to metadata
                            "source": pdf_path,
                            "filename": os.path.basename(pdf_path),  # Add filename
                            "page": page_num,
                            "type": "pdf"
                            # "upload_time": datetime.utcnow().isoformat()
                        }
                    ))

    except Exception as e:
        print(f"Error reading {pdf_path}: {str(e)}")
        return []
    return documents


# Example usage:
if __name__ == "__main__":
    # Convert PDF to documents
    pdf_docs = pdf_to_text("/shared_disk/amitv/JKTech/Samples/CSR-POLICY.pdf")

    # Chunk the PDF documents
    chunks = chunking(pdf_docs)

    print(f"Created {len(chunks)} chunks from PDF")
    print("First chunk metadata:", chunks[0].metadata)

# from langchain.text_splitter import RecursiveCharacterTextSplitter
#
#
# def chunking(data): #data is the extraction_data of sitemap_url
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1500, chunk_overlap = 300)
#     docs = text_splitter.split_documents(data)
#     return docs
#
#
# def pdf_to_text(pdf):
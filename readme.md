📄 Document Management & Q&A System
A robust RAG-based (Retrieval Augmented Generation) system that allows users to upload PDF documents, generate semantic embeddings, and query those documents using natural language.

🔧 Features
✅ Upload PDF documents and process them into vector stores

✅ Generate document embeddings using LLMs

✅ Perform semantic search and Q&A over ingested documents

✅ Select from existing documents for querying

✅ REST APIs built with FastAPI

✅ User-friendly UI with Streamlit

🚀 How to Run Locally
Backend (FastAPI)
bash
Copy
Edit
# Clone the repo
git clone https://github.com/your/repo.git
cd your-repo

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
Option 1. python3 Backend/app/api/app.py

Option 2. uvicorn app.main:app --reload --port 8503
Frontend (Streamlit)
bash
Copy
Edit
cd ../frontend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install Streamlit and other dependencies
pip install -r requirements.txt

# Run the app
go to the root directory, then run the command

streamlit run Frontend/st_app.py

⚙️ CI/CD Workflow
✅ GitHub Actions (Sample Workflow)
Create .github/workflows/ci-cd.yml

yaml
Copy
Edit
name: CI/CD Pipeline

on:
  push:
    branches: [main]

jobs:
  build-deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install Backend Dependencies
      run: |
        cd backend
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt

    - name: Lint and Test
      run: |
        cd backend
        # Optional: Add pytest or flake8 if applicable
        echo "No tests yet!"

    - name: Build Docker Image
      run: |
        docker build -t doc-qa-app .

    - name: Push to Docker Hub (optional)
      env:
        DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
        DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
      run: |
        echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin
        docker tag doc-qa-app yourusername/doc-qa-app:latest
        docker push yourusername/doc-qa-app:latest
🐳 Dockerfile
Dockerfile
Copy
Edit
# Base image
FROM python:3.10-slim

WORKDIR /app

COPY backend /app
RUN pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8503"]
☁️ Deployment Options
You can deploy this system using:

Docker Compose

AWS EC2 with Docker

Render / Railway / Heroku

Kubernetes (for scaling)

📬 APIs
/upload_pdf (POST)
Uploads a PDF, extracts and chunks text, creates vector store.

/query (POST)
Accepts a user query and a document ID to perform Q&A.

/documents (GET) ✅ (You can implement this)
Returns a list of uploaded documents (ID + Filename + Timestamp).

🧠 Technologies Used
FastAPI

LangChain + FAISS + AzureOpenAI

Streamlit

PyPDF2

Docker

GitHub Actions


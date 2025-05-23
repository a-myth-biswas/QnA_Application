from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Form, File, HTTPException, UploadFile, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import uuid
import os
import sys
import datetime
from jose import JWTError, jwt
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from Backend.app.services.llm import get_final_response
from Backend.app.db.db import db_creation
from Backend.app.services.chunking import *
from Backend.app.core.utils import create_access_token
app = FastAPI()
from dotenv import load_dotenv
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY")  # replace with a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
UPLOAD_TRACKER_FILE = os.path.join(os.path.abspath(os.curdir), "uploaded_docs.json")

fake_user = {
    "username": "admin",
    "password": "password"  # use hashed password in real scenarios
}

def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != fake_user["username"]:
            raise credentials_exception
    except JWTError:
        raise credentials_exception


class QueryRequest(BaseModel):
    query: str
    db_folder: str

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != fake_user["username"] or form_data.password != fake_user["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(SECRET_KEY, ALGORITHM, data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/documents")
def list_uploaded_documents(token: str = Depends(verify_token)):
    try:
        import json
        if not os.path.exists(UPLOAD_TRACKER_FILE):
            return []
        with open(UPLOAD_TRACKER_FILE, "r") as f:
            data = json.load(f)
        return JSONResponse(status_code=200, content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def chatbot(request: QueryRequest, token: str = Depends(verify_token)):
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query can not be empty")

        uuid_path = request.db_folder

        # Validate UUID Path exists
        if not os.path.exists(uuid_path):
            raise HTTPException(status_code=404, detail=f"Folder {uuid_path} not found")

        document_id = os.path.basename(uuid_path)
        answer = get_final_response(query, document_id)
        return {"question": query, "answer": answer}

    except HTTPException as he:
        raise he  # Let FastAPI handle it as intended

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...), token: str = Depends(verify_token)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    target_dir = None  # Declare target_dir here to be accessible in the exception handling block
    try:
        # 1. Generate a unique directory name using a UUID
        doc_id = str(uuid.uuid4())
        root_dir = os.path.abspath(os.curdir)
        target_dir = os.path.join(root_dir, doc_id)
        os.makedirs(target_dir, exist_ok=True)

        # 2. Save the uploaded PDF file in the target directory
        file_path = os.path.join(target_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 3. Extract text from the PDF file
        docs = pdf_to_text(file_path, doc_id)  # Replace with your actual extraction logic
        # 4. Process the extracted documents (chunking) and create/update the FAISS index
        chunks = chunking(docs)
        db_creation(chunks, file.filename, doc_id)
        print("db creation successfull")
        doc_metadata = {
            "document_id": doc_id,
            "filename": file.filename,
            "upload_time": datetime.datetime.now().isoformat(),
            "path": target_dir
        }
        print("metadata creation successfull")
        import json
        if os.path.exists(UPLOAD_TRACKER_FILE):
            with open(UPLOAD_TRACKER_FILE, "r") as f:
                try:
                    existing = json.load(f)
                except json.JSONDecodeError:
                    existing = []
        else:
            existing = []
        existing.append(doc_metadata)
        with open(UPLOAD_TRACKER_FILE, "w") as f:
            json.dump(existing, f, indent=4)
        print("JSON creation/dump successful")
        return JSONResponse(status_code=200, content={
            "message": "PDF processed and vector store updated successfully.",
            "pdf_folder": target_dir,
            "filename": file.filename,
            "document_id": doc_id
        })

    except Exception as e:
        # Cleanup if something goes wrong
        if target_dir and os.path.exists(target_dir):
            os.rmdir(target_dir)  # Delete the folder
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/upload_pdf")
# async def upload_pdf(file: UploadFile = File(...)):
#     try:
#         # 1. Generate a unique directory name using a UUID
#         unique_id = str(uuid.uuid4())
#         root_dir = os.path.abspath(os.curdir)
#         target_dir = os.path.join(root_dir, unique_id)
#         os.makedirs(target_dir, exist_ok=True)
#
#         # 2. Save the uploaded PDF file in the target directory
#         file_path = os.path.join(target_dir, file.filename)
#         with open(file_path, "wb") as f:
#             content = await file.read()
#             f.write(content)
#
#         # 3. Extract text from the PDF file
#         docs = pdf_to_text(file_path)  # Replace with your actual extraction logic
#         # 4. Process the extracted documents (chunking) and create/update the FAISS index
#         chunks = chunking(docs)
#         db_creation(chunks, target_dir)
#         # 5. Respond with success, including the folder and filename
#         response = {
#             "message": "PDF processed and vector store updated successfully.",
#             "pdf_folder": target_dir,
#             "filename": file.filename
#         }
#         return JSONResponse(status_code=200, content=response)
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port = 8503)
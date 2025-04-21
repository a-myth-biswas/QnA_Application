import streamlit as st
import requests

# API URLs
API_BASE_URL = "http://localhost:8503"
LOGIN_ENDPOINT = f"{API_BASE_URL}/login"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload_pdf"
QUERY_ENDPOINT = f"{API_BASE_URL}/query"
DOCUMENTS_ENDPOINT = f"{API_BASE_URL}/documents"

st.set_page_config(page_title="Doc Q&A with Auth", layout="centered")
st.title("🔐 Document Management and Q&A UI")

# Session state for auth token
if "access_token" not in st.session_state:
    st.session_state.access_token = None

# Step 0: Login Form
st.sidebar.header("🔐 Login")

with st.sidebar.form("login_form"):
    username = st.text_input("Username", value="admin")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

    if submitted:
        try:
            login_data = {"username": username, "password": password}
            res = requests.post(LOGIN_ENDPOINT, data=login_data)
            if res.status_code == 200:
                token = res.json()["access_token"]
                st.session_state.access_token = token
                st.sidebar.success("Login successful!")
            else:
                st.sidebar.error("Login failed.")
        except Exception as e:
            st.sidebar.error(f"Error during login: {e}")

# If not logged in, don't show rest
if not st.session_state.access_token:
    st.warning("Please login from the sidebar to use the app.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

# Step 1: Upload a new PDF
st.header("📤 Upload a PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    st.write("File selected:", uploaded_file.name)

    if st.button("Upload PDF"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        try:
            with st.spinner("Uploading and processing file..."):
                # response = requests.post(UPLOAD_ENDPOINT, files=files)
                response = requests.post(UPLOAD_ENDPOINT, files=files, headers=headers)

            if response.status_code == 200:
                data = response.json()
                st.success("File uploaded and processed successfully!")
                st.session_state.selected_document = data.get("pdf_folder")
            else:
                st.error(f"Upload failed: {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Step 2: Choose an existing document
st.header("📚 Choose a Document")

try:
    doc_response = requests.get(DOCUMENTS_ENDPOINT, headers=headers)
    if doc_response.status_code == 200:
        documents = doc_response.json()
        if documents:
            options = {
                f"{doc['filename']} (Uploaded: {doc['upload_time']})": doc['document_id']
                for doc in documents
            }
            selected = st.selectbox("Select a document to query", list(options.keys()))
            st.session_state.selected_document = options[selected]
        else:
            st.info("No documents found. Please upload one.")
    else:
        st.error(f"Failed to fetch documents list: {doc_response.text}")
except Exception as e:
    st.error(f"Error fetching document list: {e}")

# Step 3: Ask a Question
st.header("❓ Ask a Question")

query_text = st.text_input("Enter your query")

if "selected_document" in st.session_state:
    if st.button("Submit Query"):
        if not query_text.strip():
            st.warning("Please enter a question.")
        else:
            payload = {
                "query": query_text,
                "db_folder": st.session_state.selected_document
            }
            try:
                with st.spinner("Fetching answer..."):
                    res = requests.post(QUERY_ENDPOINT, json=payload, headers=headers)
                if res.status_code == 200:
                    result = res.json()
                    st.subheader("🧠 LLM Response")
                    st.markdown(f"**Question:** {result['question']}")
                    st.markdown(f"**Answer:** {result['answer']}")
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"An error occurred while querying: {e}")
else:
    st.info("Please select a document before asking a question.")
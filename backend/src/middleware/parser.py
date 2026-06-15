import fitz  # PyMuPDF
from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter

async def parse_resume(resume: UploadFile):
    """
    Extract text from resume (PDF or text file) and return both raw text and chunks.
    """
    file_bytes = await resume.read()

    # PDF parsing
    if resume.filename.endswith(".pdf"):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([page.get_text() for page in doc])
    else:
        # Assume plain text file
        text = file_bytes.decode("utf-8")

    # Chunking for retrieval
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)
    chunks = splitter.split_text(text)

    return text, chunks

import io
import fitz  # PyMuPDF
from fastapi import UploadFile
from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

async def parse_resume(resume: UploadFile):
    """
    Extract text from resume (PDF, DOCX, or plain text file)
    and return both raw text and chunks.
    """
    file_bytes = await resume.read()
    fname = resume.filename.lower()

    # PDF parsing
    if fname.endswith(".pdf"):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([page.get_text() for page in doc])

    # DOCX parsing
    elif fname.endswith(".docx"):
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    # Plain text parsing
    elif fname.endswith(".txt"):
        text = file_bytes.decode("utf-8")

    else:
        raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")

    # Chunking for retrieval
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)
    chunks = splitter.split_text(text)

    return text, chunks


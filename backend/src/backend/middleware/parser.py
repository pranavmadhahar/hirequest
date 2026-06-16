"""
parser.py

Resume parsing utilities.

Supported Formats:
- PDF
- DOCX
- TXT

Responsibilities:
- Extract raw text from uploaded resumes
- Normalize content into plain text
- Split text into retrieval-ready chunks for embedding
"""

import io

import fitz  # PyMuPDF
from fastapi import UploadFile
from docx import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)


async def parse_resume(
    resume: UploadFile,
) -> tuple[str, list[str]]:
    """
    Parse an uploaded resume and generate retrieval chunks.

    Args:
        resume:
            Uploaded resume file.

    Returns:
        tuple:
            (
                full_resume_text,
                list_of_resume_chunks
            )

    Raises:
        ValueError:
            If the uploaded file format is unsupported.
    """

    file_bytes = await resume.read()
    fname = resume.filename.lower()

    if fname.endswith(".pdf"):

        doc = fitz.open(
            stream=file_bytes,
            filetype="pdf",
        )

        text = "".join(
            page.get_text()
            for page in doc
        )

    elif fname.endswith(".docx"):

        doc = Document(
            io.BytesIO(file_bytes)
        )

        text = "\n".join(
            p.text
            for p in doc.paragraphs
            if p.text.strip()
        )

    elif fname.endswith(".txt"):

        text = file_bytes.decode("utf-8")

    else:
        raise ValueError(
            "Unsupported file type. "
            "Please upload PDF, DOCX, or TXT."
        )

    # Create retrieval-friendly chunks for
    # vector embedding and similarity search.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=50,
    )

    chunks = splitter.split_text(text)

    return text, chunks
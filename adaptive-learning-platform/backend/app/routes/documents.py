from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends, BackgroundTasks
from typing import List
import os
import shutil
from bson import ObjectId
from datetime import datetime

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.core.config import get_settings
from app.models.document import (
    DocumentResponse,
    DocumentListResponse,
    FileType,
    ProcessingStatus,
    DocumentMetadata
)
from app.services.document_processor import DocumentProcessor

settings = get_settings()
router = APIRouter()


async def process_document_background(document_id: str, file_path: str, file_type: FileType):
    """Background task to process uploaded document"""
    from app.core.database import get_database

    db = get_database()
    processor = DocumentProcessor()

    try:
        # Update status to processing
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"processing_status": ProcessingStatus.PROCESSING}}
        )

        # Extract text
        if file_type == FileType.PDF:
            extracted_text, total_pages = processor.extract_text_from_pdf(file_path)
        else:
            extracted_text = processor.extract_text_from_markdown(file_path)
            total_pages = None

        # Split into sections
        sections = processor.split_into_sections(
            extracted_text,
            is_markdown=(file_type == FileType.MARKDOWN)
        )

        # Calculate metadata
        word_count = processor.count_words(extracted_text)
        all_topics = list(set(topic for section in sections for topic in section.topics))

        metadata = DocumentMetadata(
            total_pages=total_pages,
            word_count=word_count,
            detected_topics=all_topics[:20]  # Top 20 topics
        )

        # Update document with processed data
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {
                "extracted_text": extracted_text,
                "sections": [s.dict() for s in sections],
                "metadata": metadata.dict(),
                "processing_status": ProcessingStatus.COMPLETED,
                "updated_at": datetime.utcnow()
            }}
        )

    except Exception as e:
        # Update with error
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {
                "processing_status": ProcessingStatus.FAILED,
                "processing_error": str(e),
                "updated_at": datetime.utcnow()
            }}
        )


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Upload and process a PDF or Markdown document"""

    # Validate file type
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in ['pdf', 'md', 'markdown']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and Markdown files are supported"
        )

    file_type = FileType.PDF if file_extension == 'pdf' else FileType.MARKDOWN

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Create upload directory if not exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Save file
    file_path = os.path.join(settings.UPLOAD_DIR, f"{user_id}_{datetime.utcnow().timestamp()}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create document record
    document = {
        "user_id": ObjectId(user_id),
        "title": file.filename.rsplit('.', 1)[0],
        "original_file_name": file.filename,
        "file_type": file_type,
        "file_path": file_path,
        "file_size": file_size,
        "extracted_text": "",
        "sections": [],
        "metadata": {},
        "processing_status": ProcessingStatus.PENDING,
        "uploaded_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = await db.documents.insert_one(document)
    document["_id"] = str(result.inserted_id)

    # Process in background
    background_tasks.add_task(
        process_document_background,
        str(result.inserted_id),
        file_path,
        file_type
    )

    return DocumentResponse(
        _id=str(result.inserted_id),
        title=document["title"],
        original_file_name=document["original_file_name"],
        file_type=file_type,
        file_size=file_size,
        sections=[],
        metadata=DocumentMetadata(word_count=0, detected_topics=[]),
        processing_status=ProcessingStatus.PENDING,
        uploaded_at=document["uploaded_at"]
    )


@router.get("/", response_model=List[DocumentListResponse])
async def get_user_documents(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get all documents for current user"""
    cursor = db.documents.find(
        {"user_id": ObjectId(user_id)}
    ).sort("uploaded_at", -1)

    documents = await cursor.to_list(length=100)

    return [
        DocumentListResponse(
            _id=str(doc["_id"]),
            title=doc["title"],
            file_type=doc["file_type"],
            processing_status=doc["processing_status"],
            uploaded_at=doc["uploaded_at"],
            sections_count=len(doc.get("sections", [])),
            word_count=doc.get("metadata", {}).get("word_count", 0)
        )
        for doc in documents
    ]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get a specific document"""
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": ObjectId(user_id)
    })

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Convert sections to proper format
    from app.models.document import Section

    sections = [Section(**s) for s in document.get("sections", [])]

    return DocumentResponse(
        _id=str(document["_id"]),
        title=document["title"],
        original_file_name=document["original_file_name"],
        file_type=document["file_type"],
        file_size=document["file_size"],
        sections=sections,
        metadata=DocumentMetadata(**document.get("metadata", {})),
        processing_status=document["processing_status"],
        processing_error=document.get("processing_error"),
        uploaded_at=document["uploaded_at"]
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Delete a document"""
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": ObjectId(user_id)
    })

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Delete file
    if os.path.exists(document["file_path"]):
        os.remove(document["file_path"])

    # Delete from database
    await db.documents.delete_one({"_id": ObjectId(document_id)})

    # Delete associated questions
    await db.questions.delete_many({"document_id": ObjectId(document_id)})

    return None

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from enum import Enum


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class FileType(str, Enum):
    PDF = "pdf"
    MARKDOWN = "markdown"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Section(BaseModel):
    title: str
    content: str
    level: int = Field(..., ge=1, le=6)
    start_index: int
    end_index: int
    topics: List[str] = []


class DocumentMetadata(BaseModel):
    total_pages: Optional[int] = None
    word_count: int
    language: str = "en"
    detected_topics: List[str] = []


class DocumentBase(BaseModel):
    title: str
    original_file_name: str
    file_type: FileType


class DocumentCreate(DocumentBase):
    pass


class DocumentInDB(DocumentBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    file_path: str
    file_size: int
    extracted_text: str
    sections: List[Section] = []
    metadata: DocumentMetadata
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    processing_error: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DocumentResponse(DocumentBase):
    id: str = Field(alias="_id")
    file_size: int
    sections: List[Section]
    metadata: DocumentMetadata
    processing_status: ProcessingStatus
    processing_error: Optional[str] = None
    uploaded_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class DocumentListResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    file_type: FileType
    processing_status: ProcessingStatus
    uploaded_at: datetime
    sections_count: int
    word_count: int

    class Config:
        populate_by_name = True

from pydantic import BaseModel
from typing import List, Optional, Dict

"""
Textract 模型
"""

class BoundingBox(BaseModel):
    Width: float
    Height: float
    Left: float
    Top: float

class Point(BaseModel):
    X: float
    Y: float

class Geometry(BaseModel):
    BoundingBox: BoundingBox
    Polygon: List[Point]

class Relationship(BaseModel):
    Type: str
    Ids: List[str] = []

class Block(BaseModel):
    BlockType: str
    Confidence: Optional[float] = None
    RowIndex: Optional[int] = None
    ColumnIndex: Optional[int] = None
    RowSpan: Optional[int] = None
    ColumnSpan: Optional[int] = None
    Text: Optional[str] = None
    Geometry: Geometry
    Id: str
    EntityTypes: Optional[List[str]] = None
    Relationships: Optional[List[Relationship]] = None
    Page: Optional[int] = 1


class DocumentMetadata(BaseModel):
    Pages: int

class ResponseMetadata(BaseModel):
    RequestId: str
    HTTPStatusCode: int
    HTTPHeaders: Optional[Dict[str, str]] = {}
    RetryAttempts: Optional[int] = None

class Textract_Response(BaseModel):
    DocumentMetadata: DocumentMetadata
    JobStatus: Optional[str] = None
    Blocks: List[Block] = []
    AnalyzeDocumentModelVersion: str
    ResponseMetadata: ResponseMetadata

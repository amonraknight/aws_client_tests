from pydantic import BaseModel
from typing import List, Optional, Union
from src.parsers.textract_schemas import Geometry


class GeneralItem(BaseModel):
    Geometry: Geometry


class IndependentLine(GeneralItem):
    BlockType: str = "LINE"
    Text: Optional[str] = None


class TableTitle(GeneralItem):
    Text: Optional[str] = None


class TableFooter(GeneralItem):
    Text: Optional[str] = None


class StructuredTable(GeneralItem):
    BlockType: str = "TABLE"
    Content: List[List[str]] = []
    TableTitle: Optional[TableTitle] = None
    TableFooter: Optional[TableFooter] = None


class KeyOfKVSet(GeneralItem):
    Text: Optional[str] = None


class ValueOfKVSet(GeneralItem):
    Text: Optional[str] = None


class KeyValueSet(BaseModel):
    BlockType: str = "KV_SET"
    # The set doesn't have a geometry.
    Key: KeyOfKVSet
    Value: ValueOfKVSet


class Page(BaseModel):
    PageIdx: int
    Items: Optional[List[Union[IndependentLine, StructuredTable, KeyValueSet]]] = []


class Document(BaseModel):
    Pages: Optional[List[Page]] = []

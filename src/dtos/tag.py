from typing import Optional
from pydantic import BaseModel, Field
from src.dtos.objectid import PydanticObjectId
from flask import jsonify

class Tag(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    name: str
    code: str

    def to_json(self):
        return jsonify(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        return data